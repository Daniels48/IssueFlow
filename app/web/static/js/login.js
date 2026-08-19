"use strict";

const form = document.getElementById("login-form");
const error = document.getElementById("error");

async function initLoginPage() {
    const user = await window.userPromise;

    if (user) {
        window.location.href = "/";
        return;
    }
}

initLoginPage();

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    error.textContent = "";

    const username = document.getElementById("username_").value.trim();
    const password = document.getElementById("password").value;
    const res = await api.post(window.data_url.login_api, {username:username, password: password});

    if (!res) {return;}

    if (!res.ok) {
        try {
            const data = await res.json();
            error.textContent = data.detail || data.message || "Invalid username or password.";
        } catch {error.textContent = "Invalid username or password.";}
        return;
    }
    window.location.href = "/";
});