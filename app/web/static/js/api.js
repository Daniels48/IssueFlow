"use strict";

let refreshPromise = null;
window.user = null;
const WS_AUTH_REQUIRED = 4001;

const user_header = document.getElementById("username");
document.getElementById("logout").addEventListener("click", window.logout);

const url_api = "/api";
const url_users = `${url_api}/users`;
const url_auth = `${url_api}/auth`;
const url_sessions = `${url_auth}/sessions`;
const getQuery = (query) => `?search=${encodeURIComponent(query)}`;

const data_url = {
    ws: `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`,

    login: `/login`,
    login_api: `${url_auth}/login`,
    register_api: `${url_auth}/register`,
    register: `/register`,

    refresh: `${url_auth}/refresh`,
    logout: `${url_auth}/logout`,
    verify_email: `${url_auth}/email/verify`,
    resend_email_code: `${url_auth}/email/resend-code`,
    change_email: `${url_auth}/email/change`,
    change_password: `${url_auth}/password-change`,
    forgot_password_request: `${url_auth}/forgot-password/request`,
    forgot_password_verify: `${url_auth}/forgot-password/verify`,
    forgot_password_reset: `${url_auth}/forgot-password/reset`,
    forgot_password_page_send: "/forgot-password-send",
    forgot_password_page_verify: "/forgot-password-verify",
    forgot_password_page_reset: "/forgot-password-reset",


    sessions: url_sessions,
    logout_other:`${url_sessions}/others`,
    revoke_session: (SessionId) => `${url_sessions}/${SessionId}`,

    me: `${url_users}/me`,
    searchUsers: (query, projectId) => `${url_users}/search${getQuery(query)}&project_id=${projectId}`,

    projects: `${url_api}/projects`,
    project: (projectId) => `${data_url.projects}/${projectId}`,

    members: (projectId) => `${data_url.project(projectId)}/members`,
    member: (projectId, userId) => `${data_url.members(projectId)}/${userId}`,

    issues: (projectId, query = "") => `${data_url.project(projectId)}/issues${query ? getQuery(query) : ""}`,
    issue: (projectId, issueId) => `${data_url.issues(projectId)}/${issueId}`,
    issueEdit: (projectId, issueId) => `${data_url.issue(projectId, issueId)}/edit`,
    issueEditStatus: (projectId, issueId) => `${data_url.issues(projectId)}/${issueId}/status`,
    issueEditPriority: (projectId, issueId) => `${data_url.issues(projectId)}/${issueId}/priority`,
    issueEditDueDate: (projectId, issueId) => `${data_url.issues(projectId)}/${issueId}/due-date`,
    issueEditAssignee: (projectId, issueId) => `${data_url.issues(projectId)}/${issueId}/assignee`,
    issueClose: (projectId, issueId) => `${data_url.issues(projectId)}/${issueId}/close`,
    issueReopen: (projectId, issueId) => `${data_url.issues(projectId)}/${issueId}/reopen`,


    comment: (projectId, issueId) => `${data_url.issue(projectId, issueId)}/comments`,
    comments: (projectId, issueId, comId) => `${data_url.comment(projectId, issueId)}/${comId}`,
};

const authPages = new Set([
    data_url.login,
    data_url.register,
    data_url.forgot_password_page_send,
    data_url.forgot_password_page_verify,
    data_url.forgot_password_page_reset,
]);

const isAuthPage = authPages.has(location.pathname);

let clientInfo = {
    language: navigator.language,
    languages: navigator.languages,

    resolution: {
        screen_width: Math.round(screen.width),
        screen_height: Math.round(screen.height),
        dpr: window.devicePixelRatio,
    },

    position: null,

    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
};

navigator.geolocation.getCurrentPosition(
    (position) => {
        clientInfo.position = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
        };

        localStorage.setItem("client_position", JSON.stringify(clientInfo.position));
    },
    (error) => {
        console.log(
            "Геолокация недоступна:",
            error.message
        );
    },
);

class WSClient {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.reconnectDelay = 3000;
        this.reconnectTimer = null;
        this.handlers = {};
        this.queue = [];
    }

    connect() {
        if (this.connected || this.socket?.readyState === WebSocket.CONNECTING) {return}
        this.socket = new WebSocket(data_url.ws);
        this.socket.onopen = () => {
            console.log("WS connected");
            this.connected = true;
            if (this.reconnectTimer) {
                clearTimeout(this.reconnectTimer);
                this.reconnectTimer = null;
            }
            while (this.queue.length) {this.socket.send(this.queue.shift())}
        };

        this.socket.onmessage = ({ data }) => {
            const event = JSON.parse(data);
            const handlers = this.handlers[event.type] ?? [];
            for (const handler of handlers) {handler(event);}
            const globalHandlers = this.handlers["*"] ?? [];
            for (const handler of globalHandlers) {handler(event);}
        };

        this.socket.onclose = async (event) => {
            console.log("WS disconnected");
            this.connected = false;
            if (event.code === WS_AUTH_REQUIRED) {
               const refreshed = await refreshToken();
                if (!refreshed) {window.location.href = data_url.login;return;}
                this.connect();
                return;
            }
            this.reconnect();
        };

        this.socket.onerror = (error) => {
            console.error(error);
            this.socket.close();
        };
    }

    reconnect() {
        if (this.reconnectTimer) {return;}
        console.log(`Reconnect in ${this.reconnectDelay / 1000}s`);
        this.reconnectTimer = setTimeout(() => {this.connect()}, this.reconnectDelay);
    }

    disconnect() {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
        this.connected = false;
        this.socket?.close();
    }

    send(data) {
        const message = JSON.stringify(data);
        if (!this.connected) {this.queue.push(message);return;}
        this.socket.send(message);
    }

    on(type, callback) {
        if (!this.handlers[type]) {this.handlers[type] = [];}
        this.handlers[type].push(callback);
    }

    off(type, callback) {
        if (!this.handlers[type]) {return;}
        this.handlers[type] = this.handlers[type].filter(handler => handler !== callback);
    }

    once(type, callback) {
        const wrapper = (event) => {
            callback(event);
            this.off(type, wrapper);
        };
        this.on(type, wrapper);
    }
}


async function request(url, options = {}) {
    const headers = new Headers(options.headers);
    const savedPosition = localStorage.getItem("client_position");

    if (savedPosition) {clientInfo.position = JSON.parse(savedPosition);}
    headers.set("X-Client-Info", JSON.stringify(clientInfo));
    return fetch(url, {
        ...options,
        headers,
        credentials: "include",
    });
}

async function apiFetch(url, options = {}) {
    const res = await request(url, options);
    if (res.status !== 401) {return res;}
    const refreshed = await refreshToken();
    if (!refreshed) {
        window.location.href = data_url.login;
        return null;
    }
    const retry = await request(url, options);
    if (retry.status === 401) {
        window.location.href = data_url.login;
        return null;
    }
    return retry;
}

const jsonOptions = (method, data = null) => ({
    method,
    headers: {"Content-Type": "application/json",},
    ...(data !== null && {body: JSON.stringify(data)}),
});

async function refreshToken() {
    if (refreshPromise) {return refreshPromise;}
    refreshPromise = (async () => {
        const res = await fetch(data_url.refresh, {method: "POST", credentials: "include"});
        return res.ok;
    })();
    try {return await refreshPromise}
    finally {refreshPromise = null}
}

async function logout() {
    await fetch(data_url.logout, {
        method: "POST",
        credentials: "include",
    });
    window.location.reload();
}

function formatRelativeDate(dateString, prefix = "") {
    if (!dateString) return "—";

    const date = new Date(dateString);
    const now = new Date();

    let duration = (date - now) / 1000;

    const divisions = [
        { amount: 60, name: "second" },
        { amount: 60, name: "minute" },
        { amount: 24, name: "hour" },
        { amount: 7, name: "day" },
        { amount: 4.34524, name: "week" },
        { amount: 12, name: "month" },
        { amount: Infinity, name: "year" },
    ];

    for (const division of divisions) {
        if (Math.abs(duration) < division.amount) {
            const result = new Intl.RelativeTimeFormat("en", {
                numeric: "auto",
            }).format(Math.round(duration), division.name);

            return prefix ? `${prefix} ${result}` : result;
        }

        duration /= division.amount;
    }
}

function formatDate(dateString, year = 0, time = false) {
    if (!dateString) return "—";

    const date = new Date(dateString);

    const dateOptions = {
        day: "numeric",
        month: "short",
    };

    if (year === 2) {
        dateOptions.year = "2-digit";
    }
    if (year === 4) {
        dateOptions.year = "numeric";
    }

    const datePart = new Intl.DateTimeFormat("en-US", dateOptions)
        .format(date);

    if (!time) {
        return datePart;
    }

    const timePart = new Intl.DateTimeFormat("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
    }).format(date);

    return `${datePart} • ${timePart}`;
}

const api = {
    get: (url) => apiFetch(url),
    post: (url, data) => apiFetch(url, jsonOptions("POST", data)),
    patch: (url, data) => apiFetch(url, jsonOptions("PATCH", data)),
    put: (url, data) => apiFetch(url, jsonOptions("PUT", data)),
    del: (url) => apiFetch(url, { method: "DELETE" }),
};

window.ws = new WSClient();

window.api = api;
window.logout = logout;
window.data_url = data_url;
window.relativeDate = formatRelativeDate;
window.formatDate = formatDate

if (!isAuthPage) {
      ws.on("*", (event) => {
        const notification = window.NotificationFactory.fromEvent(event);
        if (notification) {window.notificationCenter.add(notification);}
    });

    window.userPromise = (async () => {
        const res = await api.get(window.data_url.me);
        if (!res || !res.ok) {return null;}
        const user = await res.json();
        window.user = user;
        return user;
    })();

    window.userPromise.then(user => {
        if (!user) {window.location.replace(data_url.login);return;}
        if (user_header) {user_header.textContent = user.username;}
        window.ws.connect();
    });
}