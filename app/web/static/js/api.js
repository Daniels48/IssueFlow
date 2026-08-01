"use strict";

let refreshPromise = null;

const data_url = {
    refresh: "/api/auth/refresh",
    logout: "/api/auth/logout",
    login: "/login",
    register: "/register",
    verify_email: "/api/users/verify-email",
    resend_email_code: "/api/users/resend-email-code",
    change_email: "/api/users/email-change",

    projects: "/api/projects",
    me: "/api/users/me",
    ws: `://${location.host}/ws`,

    project: (projectId) => `${data_url.projects}/${projectId}`,

    searchUsers: (query, projectId) => `/api/users/search${getQuery(query)}&project_id=${projectId}`,

    members: (projectId) => `${data_url.project(projectId)}/members`,
    member: (projectId, userId) => `${data_url.members(projectId)}/${userId}`,

    issues: (projectId, query = "") => `${data_url.project(projectId)}/issues${query ? getQuery(query) : ""}`,
    issue: (projectId, issueId) => `${data_url.issues(projectId)}/${issueId}`,
    issueEdit: (projectId, issueId) => `${data_url.issue(projectId, issueId)}/edit`,

    comment: (projectId, issueId) => `${data_url.issue(projectId, issueId)}/comments`,
    comments: (projectId, issueId, comId) => `${data_url.comment(projectId, issueId)}/${comId}`,
};

const getQuery = (query) => `?query=${encodeURIComponent(query)}`;

async function request(url, options = {}) {
    return fetch(url, {
        ...options,
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
    headers: {
        "Content-Type": "application/json",
    },
    ...(data !== null && {
        body: JSON.stringify(data),
    }),
});

const api = {
    get: (url) => apiFetch(url),
    post: (url, data) => apiFetch(url, jsonOptions("POST", data)),
    patch: (url, data) => apiFetch(url, jsonOptions("PATCH", data)),
    put: (url, data) => apiFetch(url, jsonOptions("PUT", data)),
    del: (url) => apiFetch(url, { method: "DELETE" }),
};

async function refreshToken() {
    if (refreshPromise) {return refreshPromise;}
    refreshPromise = (async () => {
        const res = await fetch(data_url.refresh, {
            method: "POST",
            credentials: "include",
        });
        return res.ok;
    })();
    try {return await refreshPromise;}
    finally {refreshPromise = null;}
}

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
        if (this.connected || this.socket?.readyState === WebSocket.CONNECTING) {
            return;
        }

        const protocol = location.protocol === "https:" ? "wss" : "ws";
        const url_ws = `${protocol}${data_url.ws}`;

        this.socket = new WebSocket(url_ws);

        this.socket.onopen = () => {
            console.log("WS connected");

            this.connected = true;

            if (this.reconnectTimer) {
                clearTimeout(this.reconnectTimer);
                this.reconnectTimer = null;
            }

            while (this.queue.length) {
                this.socket.send(this.queue.shift());
            }
        };

        this.socket.onmessage = ({ data }) => {
            const event = JSON.parse(data);

            const handlers = this.handlers[event.type] ?? [];

            for (const handler of handlers) {
                handler(event);
            }

            const globalHandlers = this.handlers["*"] ?? [];

            for (const handler of globalHandlers) {
                handler(event);
            }
        };

        this.socket.onclose = async () => {
            console.log("WS disconnected");
            this.connected = false;

            if (await refreshToken()) {
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
        if (this.reconnectTimer) {
            return;
        }

        console.log(`Reconnect in ${this.reconnectDelay / 1000}s`);

        this.reconnectTimer = setTimeout(() => {
            this.connect();
        }, this.reconnectDelay);
    }

    disconnect() {
        clearTimeout(this.reconnectTimer);

        this.reconnectTimer = null;
        this.connected = false;

        this.socket?.close();
    }

    send(data) {
        const message = JSON.stringify(data);

        if (!this.connected) {
            this.queue.push(message);
            return;
        }

        this.socket.send(message);
    }

    on(type, callback) {
        if (!this.handlers[type]) {
            this.handlers[type] = [];
        }

        this.handlers[type].push(callback);
    }

    off(type, callback) {
        if (!this.handlers[type]) {
            return;
        }

        this.handlers[type] = this.handlers[type].filter(
            handler => handler !== callback
        );
    }

    once(type, callback) {
        const wrapper = (event) => {
            callback(event);
            this.off(type, wrapper);
        };

        this.on(type, wrapper);
    }
}

window.ws = new WSClient();


ws.on("*", (event) => {
    console.log(event)
    const notification = window.NotificationFactory.fromEvent(event);
    if (notification) {window.notificationCenter.add(notification);}
});

window.api = api;
window.logout = logout;
window.data_url = data_url;

const user_header = document.getElementById("username");
const logout_btn = document.getElementById("logout");
logout_btn.addEventListener("click", window.logout);

async function logout() {
    await fetch(data_url.logout, {
        method: "POST",
        credentials: "include",
    });
    window.location.reload();
}

async function loadUser() {
    const res = await api.get(window.data_url.me);
    if (!res) {return;}
    if (!res.ok) {
        location.href = window.data_url.login;
        return;
    }
    const user = await res.json();
    if (user_header) {user_header.textContent = user.username;}
}
const authPages = [data_url.login, data_url.register];

if (!authPages.includes(location.pathname)) {
    loadUser();
    window.ws.connect();
}