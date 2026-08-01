"use strict";

const form = document.getElementById("verify-form");
const inputs = [...document.querySelectorAll(".verify-code input")];
const resendBtn = document.getElementById("resend-code");
const submitBtn = form.querySelector("button");
const error = document.getElementById("verify-error");
const change_email = document.getElementById("change-email");

inputs[0].focus();
inputs.forEach((input, index) => {
    input.addEventListener("input", () => {
        clearError();
        input.value = input.value.replace(/\D/g, "");
        if (!input.value) {return;}
        if (index < inputs.length - 1) {inputs[index + 1].focus();}
        if (inputs.every(i => i.value.length === 1)) {form.requestSubmit();}
    });

    input.addEventListener("keydown", (e) => {
        if (e.key === "Backspace" && !input.value && index > 0) {inputs[index - 1].focus();}
        if (e.key === "ArrowLeft" && index > 0) {inputs[index - 1].focus();}
        if (e.key === "ArrowRight" && index < inputs.length - 1) {inputs[index + 1].focus();}
    });
    input.addEventListener("paste", (e) => {
        e.preventDefault();
        clearError();
        const code = e.clipboardData
            .getData("text")
            .replace(/\D/g, "")
            .slice(0, 6);

        code.split("").forEach((digit, i) => {
            if (inputs[i]) {inputs[i].value = digit;}
        });
        if (code.length === 6) {form.requestSubmit();}
    });
});
form.addEventListener("submit", verifyEmail);
resendBtn.addEventListener("click", resendCode);
change_email.addEventListener("click", change_email_func);

async function verifyEmail(e) {
    e.preventDefault();
    clearError();
    const code = inputs.map(i => i.value).join("");
    if (code.length !== 6) {
        showError("Enter the 6-digit verification code.");
        return;
    }
    setLoading(true);
    const res = await api.post(window.data_url.verify_email, {code});
    setLoading(false);
    if (!res) {return;}

    if (res.ok) {
        location.href = "/projects";
        return;
    }

    switch (res.status) {
        case 400:
            showError("Invalid verification code.");
            break;

        case 410:
            showError("Verification code has expired.");
            break;

        case 429:
            showError("Too many attempts. Please try again later.");
            break;

        default:showError("Something went wrong.");

    }
    inputs.forEach(i => i.value = "");
    inputs[0].focus();
}

async function resendCode() {
    if (resendBtn.disabled) {return;}
    clearError();
    resendBtn.disabled = true;
    const res = await api.post(window.data_url.resend_email_code, {});
    if (!res) {
        resendBtn.disabled = false;
        return;
    }

    if (!res.ok) {
        resendBtn.disabled = false;
        switch (res.status) {
            case 429:
                showError("Please wait before requesting another code.");
                break;

            default:showError("Unable to resend the code.");

        }
        return;
    }
    startCountdown(60);
}

function startCountdown(seconds) {
    resendBtn.disabled = true;
    resendBtn.textContent = `Resend code (${seconds}s)`;
    const timer = setInterval(() => {
        seconds--;
        resendBtn.textContent = `Resend code (${seconds}s)`;
        if (seconds <= 0) {
            clearInterval(timer);
            resendBtn.disabled = false;
            resendBtn.textContent = "Resend code";
        }
    }, 1000);
}

function setLoading(loading) {
    submitBtn.disabled = loading;
    inputs.forEach(input => {input.disabled = loading;});
}

function showError(text) {
    error.textContent = text;
    error.classList.remove("hidden");
}

function clearError() {
    error.textContent = "";
    error.classList.add("hidden");
}

async function change_email_func() {
    const email = prompt("Enter new email");
    if (email === null) {return;}

    if (!email.trim()) {
        alert("Email cannot be empty.");
        return;
    }

    const res = await api.patch(window.data_url.change_email, { email: email.trim() });

    if (!res) {
        alert("Unable to change email.");
        return;
    }

    if (!res.ok) {
        const error = await res.json().catch(() => null);
        alert(error?.detail ?? "Unable to change email.");
        return;
    }

    alert("Verification code has been sent to your new email.");
}