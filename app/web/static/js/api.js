"use strict";

const URL_REFRESH = "/api/auth/refresh";
const URL_LOGIN = "/login";
const URL_LOGOUT = "/api/auth/logout";
let refreshPromise = null;


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
        window.location.href = URL_LOGIN;
        return null;
    }

    const retry = await request(url, options);

    if (retry.status === 401) {
        window.location.href = URL_LOGIN;
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
        const res = await fetch(URL_REFRESH, {
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

    await fetch(URL_LOGOUT, {
        method: "POST",
        credentials: "include",
    });

    window.location.reload();

}


window.api = api;