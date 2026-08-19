"use strict";

const form = document.getElementById("reset-password-form");

const passwordInput = document.getElementById("password");
const confirmPasswordInput = document.getElementById("confirm-password");
const errorElement = document.getElementById("reset-error");

const resetToken = sessionStorage.getItem("password_reset_token");

if (!resetToken) {window.location.replace(window.data_url.forgot_password_page_send)}

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    errorElement.textContent = "";
    passwordInput.classList.remove("error");
    confirmPasswordInput.classList.remove("error");

    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    if (password !== confirmPassword) {
        errorElement.textContent = "Passwords do not match.";
        passwordInput.classList.add("error");
        confirmPasswordInput.classList.add("error");
        return;
    }

    if (password.length < 8) {
        errorElement.textContent = "Password must be at least 8 characters long.";
        passwordInput.classList.add("error");
        return;
    }

    const button = form.querySelector(".verify-button");
    button.disabled = true;

    const data = {reset_token: resetToken, new_password: password}
    const res = await api.post(window.data_url.forgot_password_reset, data);

    if (!res || !res.ok) {
        button.disabled = false;
        errorElement.textContent = "Unable to reset password. The reset link may have expired.";
        return;
    }

    sessionStorage.removeItem("password_reset_token");

    window.location.replace(window.data_url.login);
});