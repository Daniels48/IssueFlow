"use strict";

const form = document.getElementById("forgot-password-form");

form.addEventListener("submit", async (e) => {

    e.preventDefault();

    const email = document.getElementById("email").value.trim();

    const res = await api.post(
        window.data_url.reset_password,
        {email,}
    );

    if (!res || !res.ok) {
        alert("Unable to send verification code.");
        return;
    }

    location.href = `/reset-password/verify?email=${encodeURIComponent(email)}`;

});