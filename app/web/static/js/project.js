"use strict";

const path = window.location.pathname.split("/");
const projectId = path[path.length - 1];

const title = document.getElementById("project-title");
const description = document.getElementById("project-description");
const edit_btn = document.getElementById("edit-project");

const membersContainer = document.getElementById("members-list");
const issuesContainer = document.getElementById("issues");
const del_btn = document.getElementById("delete-project");
const manage_btn = document.getElementById("manage-members");
const modal = document.getElementById("members-modal");
const modal_close_btn = document.getElementById("close-btn");
const user_search_input = document.getElementById("user-search");
const res_search = document.getElementById("search-results");

const issue_new_btn = document.getElementById("create-issue");
const close_issue_modal = document.getElementById("modal-close");
const modal_issue = document.getElementById("issue-modal");
const form_issue = document.getElementById("issue-form");
const cancel_issue_form = document.getElementById("cancel_issue_form");
const member_cnt_obj = document.getElementById("members-count");
const issues_cnt_obj = document.getElementById("issues-count");
const issue_search = document.getElementById("search_issues");
const issue_assignee = document.getElementById("issue-assignee");

const filterStatus = document.querySelector("#filter-status");
const filterPriority = document.querySelector("#filter-priority");
const filterDueDate = document.querySelector("#filter-due-date");
const sortIssues = document.querySelector("#sort-issues");

const prjct_created = document.getElementById("project-created");
const project_owner = document.getElementById("project-owner");

let project_db;
let searchTimeout;
let UserSearchTimeout;

// --------- Event Managed -----------------------------------------
edit_btn.addEventListener("click", editProject);
del_btn.addEventListener("click", deleteProject);
manage_btn.addEventListener("click", manage_members);
modal_close_btn.addEventListener("click", manage_members);
modal.addEventListener("click", modal_members);
user_search_input.addEventListener('input', user_search_func);
membersContainer.addEventListener("click", delete_member);
res_search.addEventListener("click", add_member)
membersContainer.addEventListener("change", change_role);
issue_new_btn.addEventListener("click", view_new_issue);
close_issue_modal.addEventListener("click", close_issue_func);
form_issue.addEventListener("submit", createIssue);
cancel_issue_form.addEventListener("click", reset_issue_form);
modal_issue.addEventListener("click", modal_issue_func);


issue_search.addEventListener("input", () => loadIssuesDebounced(400));

filterStatus.addEventListener("change", () => loadIssuesDebounced(400));
filterPriority.addEventListener("change", () => loadIssuesDebounced(400));
filterDueDate.addEventListener("change", () => loadIssuesDebounced(400));
sortIssues.addEventListener("change", () => loadIssuesDebounced(400));
// ---------------------------------------------------------------



async function loadProject() {
    const res = await api.get(window.data_url.project(projectId));
    if (!res || !res.ok) {return;}
    const project = await res.json();
    project_db = {
        ...project,
        members: new Map(project.members.map(member => [member.user.public_id, member])),
        issues: new Map(project.issues.map(issue => [issue.public_id, issue]))
    };
    renderDetailProject();
    renderMembers();
    renderIssues(project.issues);
}

function renderDetailProject() {
    title.textContent = project_db.name;
    description.textContent = project_db.description || "No description";
    member_cnt_obj.textContent = project_db.members.size;
    issues_cnt_obj.textContent = project_db.issues.size;
    prjct_created.textContent =  window.formatDate(project_db.created_at, 4);
    project_owner.textContent = project_db.owner.username;
}

function renderMembers() {
    const members = [...project_db.members.values()];
    const roles = project_db.roles;

    if (members.length === 0) {
        membersContainer.innerHTML = `<div class="empty">No members</div>`;return;
    }

    let html = "";
    for (const member of members) {html += member_text(member)}
    membersContainer.innerHTML = html;

    function member_text(member) {
        let text_member_action = `
            <select class="role-select" data-user-id="${member.user.public_id}">${get_option(member)}</select>
            <button class="remove-btn" data-user-id="${member.user.public_id}">Remove</button>`;
        if (project_db.owner.public_id === member.user.public_id) {
            text_member_action = `<span class="owner-badge">Owner</span>`
        }

        return `<div class="member">
                    <div class="member-info"><span class="member-name">${member.user.username}</span></div>
                    <div class="member-actions">${text_member_action}</div>
                </div>`;
    }


    function get_option(member) {
        let options = "";
        const capitalize = text => text.charAt(0) + text.slice(1).toLowerCase();
        for (const role of roles) {
            options += `<option value="${role}" ${member.role === role ? "selected" : ""}>${capitalize(role)}</option>`
        }
        return options;
    }
}

function renderIssues(issues, is_add=false) {
    if (issues.length === 0) {
        issuesContainer.innerHTML = `<div class="empty">No issues</div>`;return;
    }

    let html = is_add ? issuesContainer.innerHTML : "";
    for (const issue of issues) {html += issue_text(issue);}
    issuesContainer.innerHTML = html;
    function issue_text(issue) {
      return `<a href="/projects/${projectId}/issues/${issue.public_id}" data-id="${issue.public_id}" class="issue">
                <div>
                    <h3>${issue.name ?? issue.title}</h3>
                    <span class="assignee-name">
                        Assigned to ${issue.assignee?.username ?? "Unassigned"} • 
                        Reported by ${issue.reporter.username}
                    </span>
                </div>
                <div class="badges">
                    <span class="due">${window.formatDate(issue.due_date)}</span>
                    <span class="progress">${uppercase(issue.status)}</span>
                    <span class="${issue.priority.toLowerCase()}">${uppercase(issue.priority)}</span>
                </div>
            </a>`
    }
    function uppercase(text) {return text.toUpperCase();}
}



// --------- Issue Managed -----------------------------------------
function modal_issue_func(event) {
   if (event.target === modal_issue) {
       modal_issue.classList.add("hidden");
       form_issue.reset();
   }
}

function reset_issue_form(event) {
    event.preventDefault();
    form_issue.reset();
}

async function createIssue(event) {
    event.preventDefault();

    const option = issue_assignee.selectedOptions[0];

    const publicId = option?.dataset.id ?? null;

    const data = {
        title: document.getElementById("issue-title").value,
        description: document.getElementById("issue-description").value || null,
        assignee_id: publicId,
        priority: document.getElementById("issue-priority").value,
        due_date: document.getElementById("issue-date").value || null,
    };

    const response = await window.api.post(window.data_url.issues(projectId), data);
    if (!response.ok) return;
    form_issue.reset();

    issues_cnt_obj.textContent = Number(issues_cnt_obj.textContent) + 1;
}

function close_issue_func(event) {
    modal_issue.classList.add("hidden");
    form_issue.reset()
}

async function view_new_issue(event) {
    const response = await window.api.get(window.data_url.members(projectId));
    if (!response.ok) {return;}
    const members = await response.json();

    let html =  `<option value="" selected disabled>Choose member</option>`;

    for (const member of members) {html += member_text(member);}

    issue_assignee.innerHTML = html;

    function member_text(member) {
        return `<option data-id="${member.user.public_id}">${member.user.username}</option>`
    }

    modal_issue.classList.remove("hidden");
}

function updateFiltersUrl(filters) {
    const params = new URLSearchParams();

    for (const [key, value] of Object.entries(filters)) {
        if (value && (key !== "search" || value.length >= 2)) {
            params.set(key, value);
        }
    }

    const query = params.toString();

    const url = query
        ? `${window.location.pathname}?${query}`
        : window.location.pathname;

    history.replaceState(null, "", url);
}

function restoreFilters() {
    const params = new URLSearchParams(window.location.search);

    issue_search.value = params.get("search") ?? "";
    filterStatus.value = params.get("status") ?? "";
    filterPriority.value = params.get("priority") ?? "";
    filterDueDate.value = params.get("due_date") ?? "";
    sortIssues.value = params.get("sort") ?? "";
}

async function loadIssues (){
    const search = issue_search.value.trim();

    const filters = {
        search: search.length >= 2 ? search : "",
        status: filterStatus.value,
        priority: filterPriority.value,
        due_date: filterDueDate.value,
        sort: sortIssues.value,
    };

    updateFiltersUrl(filters);

    const response = await window.api.get(window.data_url.issues(projectId, filters));
    if (!response.ok) return;

    const issues = await response.json();

    renderIssues(issues);
}

function loadIssuesDebounced(time = 400) {
    clearTimeout(searchTimeout);

    searchTimeout = setTimeout(loadIssues, time);
}

// -----------------------------------------------------------------



// --------- Project Managed ---------------------------------------
async function editProject() {
    const titleInput = prompt("Project title");
    if (titleInput === null) {return;}
    const title = titleInput.trim();
    const description = prompt("Description (optional)")?.trim() ?? "";
    const res = await api.patch(
        window.data_url.project(projectId), {name: title, description: description}
    );
    if (!res || !res.ok) {alert("Failed to edit project.");return;}
    loadProject();
}

async function deleteProject() {
    const res = await api.del(`${window.data_url.projects}/${projectId}`);
    if (!res || !res.ok) {
        alert("Failed to delete project.");
        return;
    }
    window.location.href = "/projects";
}
// -----------------------------------------------------------------



// --------- Member Managed ---------------------------------------
async function change_role(event) {
    const select = event.target.closest(".role-select");
    if (!select) return;
    const userId = select.dataset.userId;
    const role = select.value;
    const response = await window.api.patch(window.data_url.member(projectId, userId), {role: role})
    if (!response.ok) {return;}
    const member = await response.json();
    project_db.members.set(member.user.public_id, member);
    renderMembers();
}

async function delete_member(event) {
    const button = event.target.closest(".remove-btn");
    if (!button) return;
    const userId = button.dataset.userId;
    const response = await window.api.del(window.data_url.member(projectId, userId));
    if (response.status !== 204) {return;}
    project_db.members.delete(userId);
    renderMembers();
    renderDetailProject();
}

async function add_member(event) {
    const btn_add = event.target.closest(".add-btn");
    if (!btn_add) return;
    const user_id = btn_add.dataset.userId;
    const response = await window.api.post(window.data_url.members(projectId), {user_public_id: user_id});
    if (!response.ok) {return;}
    const member = await response.json();
    project_db.members.set(member.user.public_id, member);
    renderMembers();
    renderDetailProject();

    user_search_input.value = "";
    updateSearchResults("clear");
}

function updateSearchResults(command, html = "") {
    switch (command) {
        case "clear":res_search.classList.add("hidden");res_search.innerHTML = "";break;
        case "render":res_search.innerHTML = html;break;
        case "show":res_search.classList.remove("hidden");break;
    }
}

async function user_search_func(event) {
    const query = event.target.value.trim();
    if (query.length < 2) {
        updateSearchResults("clear")
        return;
    }
    clearTimeout(UserSearchTimeout);
    UserSearchTimeout = setTimeout(async () => {
        const users = await load(query)
        let html = "";

        for (const user of users) {html += create_user_text(user);}
        res_search.innerHTML = html;
    }, 400);


    function create_user_text(user) {
        return `<div class="search-item" >
                    <span class="search-user" data-user-id="${user.public_id}">${user.username}</span>
                    <button class="btn-primary add-btn" data-user-id="${user.public_id}">Add</button>
                </div >`
    }

    async function load(query) {
        const response = await window.api.get(window.data_url.searchUsers(query, projectId));

        if (!response.ok) {return;}
        else { res_search.classList.remove("hidden") }
        return  await response.json();
    }
}

function manage_members() {modal.classList.toggle("hidden")}

function modal_members(e) { if (e.target === modal) {modal.classList.add("hidden")}}

// ----------------------------------------------------------------

loadProject();
restoreFilters();
// loadIssues();