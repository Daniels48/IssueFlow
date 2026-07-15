"use strict";

const username = document.getElementById("username");
const email = document.getElementById("email");
const avatar = document.getElementById("avatar");

const publicId = document.getElementById("public_id");
const created = document.getElementById("created_at");
const verified = document.getElementById("verified");
const status = document.getElementById("status");

document.getElementById("logout").addEventListener("click", window.logout);

async function loadProfile() {

    const res = await api.get(window.data_url.me);

    if (!res) return;

    if (!res.ok) {
        location.href = window.data_url.login;
        return;
    }

    const user = await res.json();

    username.textContent = user.username;

    email.textContent = user.email;

    avatar.textContent =
        user.username.charAt(0).toUpperCase();

    publicId.textContent = user.public_id;

    created.textContent =
        new Date(user.created_at).toLocaleString();

    verified.textContent =
        user.email_verified_at
            ? new Date(user.email_verified_at).toLocaleString()
            : "No";

    status.textContent =
        user.is_active
            ? "Active"
            : "Inactive";
}

loadProfile();