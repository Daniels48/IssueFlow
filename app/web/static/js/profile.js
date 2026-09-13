"use strict";

const user_data = document.getElementById("user_text");
const email = document.getElementById("email");
const avatar = document.getElementById("avatar");

const publicId = document.getElementById("public_id");
const created = document.getElementById("created_at");
const verified = document.getElementById("verified");
const status = document.getElementById("status");
const session_list = document.getElementById("sessions-list");
const count_session = document.getElementById("count-session");
const revoke_all_btn = document.getElementById("revoke-all-btn");
const change_email = document.getElementById("change-email-btn");
const email_user = document.getElementById("email-user");
const password_changed_at = document.getElementById("password-changed-at");

session_list.addEventListener("click", revoke_action_session);
revoke_all_btn.addEventListener("click", revoke_all_sessions)
change_email.addEventListener("click", change_email_func);


const number = parseInt(count_session.innerText.match(/\d+/)[0]);

revoke_all_btn.disabled = number < 2;

async function revoke_all_sessions(event) {
    const res = await api.del(window.data_url.logout_other);
    if (!res) return;
    if (!res.ok) {
        alert("Error revoke session all")
        return;
    }
    while (session_list.children.length > 1) {session_list.lastElementChild.remove();}
    set_count_session(1)
}

async function revoke_action_session(event) {
    const target_element = event.target;
    const btn_revoke = target_element.classList.contains("session-revoke-btn");
    if (!btn_revoke) {return;}
    const container = target_element.closest("div.session-item");
    const sessionId = target_element.dataset.id;

    const res = await api.del(window.data_url.revoke_session(sessionId));
    if (!res) return;
    if (!res.ok) {
        alert("Error revoke session")
        return;
    }
    container.remove()
    const number = parseInt(count_session.innerText.match(/\d+/)[0]);
    if (number < 3) {
        revoke_all_btn.disabled = true;
    }
    set_count_session(number - 1)
    alert("Session delete success!")
}

function SessionHtml(session) {
    function is_current(session) {
        if (!session.is_current) {return "";}
        return `<span class="current-session">Current</span>`;
    }

    function set_device_type(session) {
        switch (session.device_type) {
            case "desktop":
                return "🖥️";

            case "mobile":
                return "📱";

            case "tablet":
                return "📱";

            default:
                return "❓";
        }
    }

    function set_browser_type(session) {
        if (session.browser) {return session.browser;}
        else {return "Chrome"}
    }

    function set_os_type(session) {
        if (session.os) {return session.os}
        else {return "Windows"}
    }

    function formatDistance(meters) {
        if (meters >= 1000) {
            return `${Math.round(meters / 1000).toLocaleString("ru-RU")} км`;
        }

        return `${Math.round(meters)} м`;
    }

    function formatCountry(country) {
        if (country === "Russian Federation") {
            return "Russia";
        }

        return country || "";
    }

    function set_geo_data(session) {
    if (!session.country) {
        return "";
    }

    const country = formatCountry(session.country);

    const location = [
        session.city,
        session.state,
        country
    ].filter(Boolean).join(", ");

    const accuracy = session.accuracy
        ? ` · ±${formatDistance(session.accuracy)}`
        : "";

    return `🌍 ${location}${accuracy}`;
}

    function set_ip_address(session) {
        if (session.ip_address) {return session.ip_address;}
        else {return "192.168.1.15"}
    }
    return `
        <div class="session-item">
            <div class="session-info">
            
                <div class="session-device">
                    ${set_device_type(session)}
                    ${set_browser_type(session)}
                    · ${set_os_type(session)}
                    ${is_current(session)}
                </div>

                <div class="session-device">${set_geo_data(session)}</div>
                
                <span class="session-meta">
                    ${set_ip_address(session)} · ${window.relativeDate(session.updated_at)}
                </span>
            </div>
    
            ${!session.is_current ? `<button class="session-revoke-btn" data-id="${session.public_id}">Revoke</button>` : ""}
        </div>
    `;
}

function change_date_change_password(date) {
    password_changed_at.innerText = `Last changed: ${window.relativeDate(date)}`
}

function renderSession(session_list){
    let html = ``;
    let current = ``;
    let any_session = ``;
    for (const session of session_list) {
        if (session.is_current) {current = SessionHtml(session)}
        else {any_session += SessionHtml(session);}
        html = current + any_session;
    }
    return html;
}

function set_count_session(count) {
    count_session.innerText = `Active sessions (${count})`
}

async function loadProfile() {
    window.userPromise.then(user => {
        if (!user) {
            window.location.href = window.data_url.login;
            return;
        }
        user_data.textContent = user.username;
        email.textContent = user.email;
        avatar.textContent = user.username.charAt(0).toUpperCase();
        publicId.textContent = user.public_id;
        created.textContent = window.formatDate(user.created_at, 4);
        verified.textContent = user.email_verified_at ? "Yes" : "No";
        status.textContent = user.is_active ? "Active" : "Inactive";
        const verify_btn = document.getElementById("verify-email-btn");
        email_user.textContent = user.email;
        change_date_change_password(user.password_changed_at);

        if (user.email_verified_at) {verify_btn.classList.add("hidden");
        } else {verify_btn.classList.remove("hidden")}

        verify_btn.addEventListener("click", () => {location.href = "/verify-email";});
    });

    const list_session = await api.get(window.data_url.sessions);
    if (!list_session) return;
    if (!list_session.ok) {
        location.href = window.data_url.login;
        return;
    }
    const sessions = await list_session.json();

    session_list.insertAdjacentHTML("beforeend", renderSession(sessions));
    set_count_session(sessions.length)
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

loadProfile();