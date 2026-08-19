"use strict";

const form = document.getElementById("reset-password-verify-form");
const emailElement = document.getElementById("user-email");
const inputs = [...document.querySelectorAll(".verify-code input")];
const resendButton = document.getElementById("resend-code");

const params = new URLSearchParams(window.location.search);
const email = params.get("email");

if (!email) {window.location.replace(window.data_url.forgot_password_page_send);}

emailElement.textContent = email;

inputs.forEach((input, index) => {
    input.addEventListener("input", () => {
        input.value = input.value.replace(/\D/g, "");
        if (input.value && index < inputs.length - 1) {inputs[index + 1].focus();}
    });

    input.addEventListener("keydown", (event) => {
        if (event.key === "Backspace" && !input.value && index > 0) {inputs[index - 1].focus()}
    });

});

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const code = inputs.map(input => input.value).join("");

    if (code.length !== 6) {alert("Enter the 6-digit verification code.");return}

    const res = await api.post(window.data_url.forgot_password_verify, {email: email, code: code});

    if (!res || !res.ok) {alert("Invalid or expired verification code.");return}

    const data = await res.json();

    sessionStorage.setItem("password_reset_token", data.reset_token);

    window.location.href = window.data_url.forgot_password_page_reset;
});


resendButton.addEventListener("click", async () => {
    resendButton.disabled = true;
    const res = await api.post(window.data_url.forgot_password_request, {email: email});

    if (!res || !res.ok) {
        alert("Unable to resend verification code.");
        resendButton.disabled = false;
        return;
    }

    alert("If an account with this email exists, we've sent a new verification code.");

    setTimeout(() => {resendButton.disabled = false}, 60000);
});