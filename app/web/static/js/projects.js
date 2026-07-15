"use strict";

const username = document.getElementById("username");
const projectsContainer = document.getElementById("projects");

document.getElementById("logout").addEventListener("click", window.logout);

// document
//     .getElementById("create-project")
//     .addEventListener("click", () => {
//         alert("Create project");
//     });

async function loadUser() {
    const res = await api.get(window.data_url.me);
    if (!res) {return;}
    if (!res.ok) {
        // location.href = "/login";
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
                <footer> <span>Created${formatDate(project.created_at)}</span> </footer>
            </article>
        `)
        .join("");

    document
        .querySelectorAll(".project-card")
        .forEach(card => {
            card.addEventListener("click", () => {
                location.href =
                    `/projects/${card.dataset.id}`;
            });
        });

}

function formatDate(date) {
    return new Date(date).toLocaleDateString();
}

async function init() {
    await loadUser();
    // await loadProjects();
}

init();