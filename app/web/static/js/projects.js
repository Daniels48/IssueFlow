"use strict";

const username = document.getElementById("username");
const projectsContainer = document.getElementById("projects");

document.getElementById("logout").addEventListener("click", window.logout);
document.getElementById("create-project").addEventListener("click", create_project);

async function create_project(){
    const title = prompt("Project title").trim();
    if (title === null) {return;}
    const description = prompt("Description (optional)").trim();
    if (description === null) {return;}
    const res = await api.post(window.data_url.projects, {name: title, description: description});
    if (!res || !res.ok) {
        alert("Failed to create project.");
        return;
    }
    loadProjects();
}

async function loadUser() {
    const res = await api.get(window.data_url.me);
    if (!res) {return;}
    if (!res.ok) {
        location.href = window.data_url.login;
        return;
    }
    const user = await res.json();
    username.textContent = user.username;
}

async function loadProjects() {
    const res = await api.get(window.data_url.projects);
    if (!res) {return;}
    if (!res.ok) {return;}
    const projects = await res.json();
    renderProjects(projects);
}

function renderProjects(projects) {
    if (projects.length === 0) {
        projectsContainer.innerHTML = `
            <div class="empty">
                <h2>No projects yet</h2>
                <p>Create your first project.</p>
            </div>
        `;
        return;
    }

    projectsContainer.innerHTML = projects
        .map(project => `
            <article class="project-card" data-id="${project.public_id}">
                <div class="project-top">
                    <div>
                        <h2>${project.name}</h2>
                        <p>${project.description ?? "No description"}</p>
                    </div>
                </div>

                <div class="stats">
                    <div>
                        <strong>${project.issues_count}</strong>
                        <span>Issues</span>
                    </div>
                    <div>
                        <strong>${project.members_count}</strong>
                        <span>Members</span>
                    </div>
                    <div>
                        <strong>${project.comments_count}</strong>
                        <span>Comments</span>
                    </div>
                </div>

                <footer>
                    <span>Owner:<strong>${project.owner}</strong></span>
                    <span>${formatDate(project.updated_at)}</span>
                </footer>
            </article>
        `)
        .join("");
}

projectsContainer.onclick = (e) => {
    const card = e.target.closest(".project-card");

    if (!card) {
        return;
    }

    location.href = `/projects/${card.dataset.id}`;
};


function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();

    let text = "Updated";

    const diffMs = now - date;
    const diffMinutes = Math.floor(diffMs / 1000 / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMinutes < 1) return `${text} just now`;
    if (diffMinutes < 60) return `${text} ${diffMinutes}m ago`;
    if (diffHours < 24) return `${text} ${diffHours}h ago`;
    if (diffDays === 1) return `${text} yesterday`;
    if (diffDays < 30) return `${text} ${diffDays} days ago`;

    return `${text} ${date.toLocaleDateString()}`;
}


async function init() {
    await loadUser();
    await loadProjects();
}

init();