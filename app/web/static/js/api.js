"use strict";

let refreshPromise = null;



const data_url = {
    refresh: "/api/auth/refresh",
    logout: "/api/auth/logout",
    login: "/login",
    register: "/register",

    projects: "/api/projects",
    me: "/api/users/me",

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

    if (res.status !== 401) {
        return res;
    }

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
    if (refreshPromise) {
        return refreshPromise;
    }

    refreshPromise = (async () => {
        const res = await fetch(data_url.refresh, {
            method: "POST",
            credentials: "include",
        });

        return res.ok;
    })();

    try {
        return await refreshPromise;
    } finally {
        refreshPromise = null;
    }
}
async function logout() {

    await fetch(data_url.logout, {
        method: "POST",
        credentials: "include",
    });

    window.location.reload();

}


window.api = api;
window.logout = logout;
window.data_url = data_url;