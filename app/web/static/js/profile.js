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

session_list.addEventListener("click", revoke_action_session);
revoke_all_btn.addEventListener("click", revoke_all_sessions)

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

function formatRelativeDate(dateString) {
        if (!dateString) return "—";

        const date = new Date(dateString);
        const now = new Date();

        const seconds = Math.floor((date - now) / 1000);

        const divisions = [
            { amount: 60, name: "second" },
            { amount: 60, name: "minute" },
            { amount: 24, name: "hour" },
            { amount: 7, name: "day" },
            { amount: 4.34524, name: "week" },
            { amount: 12, name: "month" },
            { amount: Number.POSITIVE_INFINITY, name: "year" },
        ];

        let duration = seconds;

        for (const division of divisions) {
            if (Math.abs(duration) < division.amount) {
                return new Intl.RelativeTimeFormat("en", {
                    numeric: "auto",
                }).format(Math.round(duration), division.name);
            }

            duration /= division.amount;
        }
    }

async function revoke_action_session(event) {
    const target_element = event.target;
    const btn_revoke = target_element.classList.contains("session-revoke-btn");
    if (!btn_revoke) {return;}
    const container = target_element.closest("div.session-item");
    const sessionId = target_element.dataset.id;

    const res = await api.post(window.data_url.revoke_session(sessionId));
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
}

function SessionHtml(session) {
    function is_current(session) {
        if (!session.is_current) {return "";}
        return `<span class="current-session">Current</span>`;
    }

    function set_device_type(session) {
        if (session.user_agent) {return "🖥";}
        else {return "🖥"}
    }

    function set_browser_type(session) {
        if (session.user_agent) {return "Chrome";}
        else {return "Chrome"}
    }

    function set_os_type(session) {
        if (session.user_agent) {return "Windows";}
        else {return "Windows"}
    }

    function set_ip_address(session) {
        if (session.user_agent) {return "192.168.1.15";}
        else {return "192.168.1.15"}
    }
    return `
       <div class="session-item">
            <div class="session-info">
                <div class="session-device">${set_device_type(session)} ${set_browser_type(session)} · ${set_os_type(session)} ${is_current(session)}</div>
                <span class="session-meta">${set_ip_address(session)} · ${formatRelativeDate(session.updated_at)}</span>
            </div>
            ${!session.is_current ? `<button class="session-revoke-btn" data-id="${session.public_id}">Revoke</button>` : ""}
        </div>`;
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
        created.textContent = new Date(user.created_at).toLocaleString();
        verified.textContent =
            user.email_verified_at
                ? new Date(user.email_verified_at).toLocaleString()
                : "No";

        status.textContent = user.is_active
                ? "Active"
                : "Inactive";


        const verifyContainer = document.getElementById("verify-email-container");

        // if (window.user.email_verified) {
        //     verified.textContent = "Yes";
        //     verifyContainer.classList.add("hidden");
        // } else {
        //     verified.textContent = "No";
        //     verifyContainer.classList.remove("hidden");
        //
        // }

        document.getElementById("verify-email-btn")
        .addEventListener("click", () => {
            location.href = "/verify-email";
        });
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

loadProfile();