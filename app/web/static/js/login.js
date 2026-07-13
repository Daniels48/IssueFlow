"use strict";

const form = document.getElementById("login-form");
const error = document.getElementById("error");

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    error.textContent = "";

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    const res = await api.post("/api/auth/login", {username:username, password: password});

    if (!res) {return;}

    if (!res.ok) {
        try {
            const data = await res.json();
            error.textContent =
                data.detail ||
                data.message ||
                "Invalid username or password.";

        } catch {error.textContent = "Invalid username or password.";}
        return;
    }
    window.location.href = "/";
});