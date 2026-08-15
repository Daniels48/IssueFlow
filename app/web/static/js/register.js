"use strict";

const form = document.getElementById("register-form");
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

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const repeatPassword = document.getElementById("repeat-password").value;

    if (password !== repeatPassword) {
        error.textContent = "Passwords do not match.";
        return;
    }

    const res = await api.post(window.data_url.register_api, {username: username, email: email, password: password});

    if (!res) {return;}

    if (!res.ok) {
        const data = await res.json();

        error.textContent =
            data.detail ||
            data.message ||
            "Registration failed.";

        return;
    }

    window.location.href = "/login";
});