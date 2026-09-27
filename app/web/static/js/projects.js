"use strict";

const projectsContainer = document.getElementById("projects");
let projects_db = false;

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
}

async function loadProjects() {
    const res = await api.get(window.data_url.projects);
    if (!res) {return;}
    if (!res.ok) {return;}
    const projects = await res.json();
    projects_db = new Map(projects.map(project => [project.public_id, project]));
    renderProjects();
}

function renderProjects() {
    const projects = [...projects_db.values()];
    if (projects.length === 0) {
        projectsContainer.innerHTML = `
            <div class="empty">
                <h2>No projects yet</h2>
                <p>Create your first project.</p>
            </div>
        `;
        return;
    }

    projectsContainer.innerHTML = projects.map(project => get_element(project)).join("");

    function get_element(project) {
        return `<article class="project-card" data-id="${project.public_id}">
                    <div class="project-top">
                        <div>
                            <h2>${project.name}</h2>
                            <p>${project.description || "No description"}</p>
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
                        <span>Owner:<strong>${project.owner.username}</strong></span>
                        <span>${window.relativeDate(project.updated_at, "Updated")}</span>
                    </footer>
                </article>`
    }
}

projectsContainer.onclick = (e) => {
    const card = e.target.closest(".project-card");
    if (!card) {return;}
    location.href = `/projects/${card.dataset.id}`;
};

async function init() {
    await loadProjects();
}

function all_project_event(event) {
    const handlers = {
        "project.created": new_project,
        "project.updated": update_project,
        "project.deleted": delete_project,

        "project.member.added": member_add,
        "project.member.removed": member_delete,

        "issue.created": issue_new,
        "issue.deleted": issue_delete,

        "issue.comment.created": comment_new,
        "issue.comment.deleted": comment_delete ,
    }
    function create_project_data(data) {
        return {
            public_id: data.project.public_id,
            name: data.project.name,
            description: data.project.description,
            updated_at: data.occurred_at,

            owner: {
                public_id: data.project.owner.public_id,
                username: data.project.owner.username,
            },

            members_count: data.project.members_count ?? 1,
            issues_count: data.project.issues_count ?? 0,
            comments_count: data.project.comments_count ?? 0,
        };
    }

    function new_project(event) {
        const data = event.payload;
        const new_project = create_project_data(data)
        projects_db = new Map([[new_project.public_id, new_project], ...projects_db,]);
        renderProjects();
    }

    function update_project(event) {
        const data = event.payload;
        const project = projects_db.get(data.project.public_id);
        if (!project) {return;}

        project.updated_at = data.occurred_at;
        project.name = data.project.name;
        project.description = data.project.description;

        renderProjects();
    }

    function delete_project(event) {
        const data = event.payload;
        projects_db.delete(data.project.public_id);
        renderProjects();
    }

    function updateProjectCount(event, field, delta) {
        const data = event.payload;
        const project = projects_db.get(data.project.public_id);
        if (!project) {return;}
        project.updated_at = data.occurred_at;
        project[field] += delta;
        renderProjects();
    }

    function member_add(event) {
        if (window.user?.public_id === event.payload.user?.public_id) {
            const data = event.payload;
            console.log(data);
            const add_project = create_project_data(data)
            projects_db = new Map([[add_project.public_id, add_project], ...projects_db,]);
            renderProjects();
        }
    }

    function member_delete(event) {
        const data = event.payload;

        if (window.user?.public_id === data.user?.public_id) {
            projects_db.delete(data.project.public_id);
            renderProjects();
            return;
        }

        updateProjectCount(event, "members_count", -1);
    }

    function issue_new(event) {updateProjectCount(event, "issues_count", 1);}
    function issue_delete(event) {updateProjectCount(event, "issues_count", -1);}
    function comment_new(event) {updateProjectCount(event, "comments_count", 1);}
    function comment_delete(event) {updateProjectCount(event, "comments_count", -1);}

    const handler = handlers[event.event_type];
    if (handler) {handler(event);}
}

window.appEvents.on("*", (event) => {
    const handler = all_project_event;
    if (handler) {handler(event);}
});

init();