"use strict";

const form = document.getElementById("forgot-password-form");

form.addEventListener("submit", async (e) => {

    e.preventDefault();

    const email = document.getElementById("email").value.trim();

    const res = await api.post(window.data_url.forgot_password_request, {email});

    if (!res || !res.ok) {
        alert("Unable to send verification code.");
        return;
    }

    alert(" If an account with this email exists, we've sent a verification code.")

    const url = new URL(
        window.data_url.forgot_password_page_verify,
        window.location.origin,
    );

    url.searchParams.set("email", email);

    window.location.href = url.toString();
});