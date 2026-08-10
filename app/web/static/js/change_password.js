"use strict";

const form = document.getElementById("change-password-form");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const current = document.getElementById("current-password").value;
    const password = document.getElementById("new-password").value;
    const confirm = document.getElementById("confirm-password").value;

    if (password !== confirm) {
        alert("Passwords do not match.");
        return;
    }

    const res = await api.post(
        window.data_url.change_password,
        {
            current_password: current,
            password: password,
        }
    );
    if (!res || !res.ok) {
        alert("Unable to change password.");
        return;
    }
    alert("Password changed successfully.");
    form.reset();
});