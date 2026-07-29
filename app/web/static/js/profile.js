"use strict";

const user_data = document.getElementById("user_text");
const email = document.getElementById("email");
const avatar = document.getElementById("avatar");

const publicId = document.getElementById("public_id");
const created = document.getElementById("created_at");
const verified = document.getElementById("verified");
const status = document.getElementById("status");



async function loadProfile() {
    const res = await api.get(window.data_url.me);
    if (!res) return;
    if (!res.ok) {
        location.href = window.data_url.login;
        return;
    }
    const user = await res.json();
    console.log(user.username)
    console.log(user_data)
    user_data.textContent = user.username;
    email.textContent = user.email;
    avatar.textContent = user.username.charAt(0).toUpperCase();
    publicId.textContent = user.public_id;
    created.textContent = new Date(user.created_at).toLocaleString();
    verified.textContent =
        user.email_verified_at
            ? new Date(user.email_verified_at).toLocaleString()
            : "No";

    status.textContent =
        user.is_active
            ? "Active"
            : "Inactive";


    const verifyContainer = document.getElementById("verify-email-container");

    if (user.email_verified) {
        verified.textContent = "Yes";
        status.textContent = "Verified";
        verifyContainer.classList.add("hidden");
    } else {
        verified.textContent = "No";
        status.textContent = "Email not verified";
        verifyContainer.classList.remove("hidden");

    }

    document.getElementById("verify-email-btn")
    .addEventListener("click", () => {
        location.href = "/verify-email";
    });
}

loadProfile();