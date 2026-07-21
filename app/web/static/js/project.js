"use strict";

const path = window.location.pathname.split("/");
const projectId = path[path.length - 1];

const title = document.getElementById("project-title");
const description = document.getElementById("project-description");
const edit_btn = document.getElementById("edit-project");

const membersContainer = document.getElementById("members-list");
const issuesContainer = document.getElementById("issues");
const logout_btn = document.getElementById("logout");
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


// --------- Event Managed -----------------------------------------
edit_btn.addEventListener("click", editProject);
logout_btn.addEventListener("click", window.logout);
del_btn.addEventListener("click", deleteProject);
manage_btn.addEventListener("click", manage_members);
modal_close_btn.addEventListener("click", manage_members);
modal.addEventListener("click", modal_members);
user_search_input.addEventListener('input', user_search);
membersContainer.addEventListener("click", delete_member);
res_search.addEventListener("click", add_member)
membersContainer.addEventListener("change", change_role);
issue_new_btn.addEventListener("click", view_new_issue);
close_issue_modal.addEventListener("click", close_issue_func);
form_issue.addEventListener("submit", createIssue);
cancel_issue_form.addEventListener("click", reset_issue_form);
modal_issue.addEventListener("click", modal_issue_func);
issue_search.addEventListener("input", issueSearch);
// ---------------------------------------------------------------



async function loadProject() {
    const res = await api.get(window.data_url.project(projectId));
    if (!res || !res.ok) {return;}
    const project = await res.json();
    renderDetailProject(project);
    renderMembers(project.members, project.roles);
    renderIssues(project.issues);
}

function renderDetailProject(project) {
    const prjct_created = document.getElementById("project-created");
    const project_owner = document.getElementById("project-owner");
    title.textContent = project.name;
    description.textContent = project.description ?? "No description";

    member_cnt_obj.textContent = project.members.length;
    issues_cnt_obj.textContent = project.issues.length;
    prjct_created.textContent =  formatDate(project.created_at);
    project_owner.textContent = project.owner;

    function formatDate(dateString) {
    if (!dateString) return "—";

    return new Intl.DateTimeFormat("en", {
        day: "numeric",
        month: "short",
        year: "2-digit",
    }).format(new Date(dateString));
}
}

function renderMembers(members, roles, is_add=false) {
    if (members.length === 0) {
        membersContainer.innerHTML = `<div class="empty">No members</div>`;
    }
    else {
        let html = is_add ? membersContainer.innerHTML : "";
        for (const user of members) {html += member_text(user);}
        membersContainer.innerHTML = html;
        function member_text(user) {
            let text_member_action = `<span class="owner-badge">Owner</span>`;
            if (user.role !== "owner") {
                text_member_action = `<select class="role-select" data-user-id="${user.public_id}">${get_option(roles, user)}</select>
                                      <button class="remove-btn" data-user-id="${user.public_id}">Remove</button>`}

              return `<div class="member">
                        <div class="member-info"><span class="member-name">${user.username}</span></div>
                        <div class="member-actions">${text_member_action}</div>
                    </div>`
            }
        function get_option(roles, user) {
            let options = "";
            function capitalize(text) {return text.charAt(0) + text.slice(1).toLowerCase();}
            for (const role of roles) {
                options += `<option value="${role}" ${user.role === role ? "selected" : ""}>${capitalize(role)}</option>`;
            }
            return options
        }
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
                    <span>
                        Assigned to ${issue.assignee?.username ?? "Unassigned"} • 
                        Reported by ${issue.reporter.username}
                    </span>
                </div>
                <div class="badges">
                    <span class="due">${formatDate(issue.due_date)}</span>
                    <span class="progress">${uppercase(issue.status)}</span>
                    <span class="high">${uppercase(issue.priority)}</span>
                </div>
            </a>`
    }

    function uppercase(text) {return text.toUpperCase();}

    function formatDate(dateString) {
        if (!dateString) return "—";
        return new Intl.DateTimeFormat("en", {day: "numeric", month: "short",
        }).format(new Date(dateString));
    }
}



// --------- Issue Managed -----------------------------------------
async function issueSearch(event) {
    let query = event.target.value.trim();
    query =query.length >= 2 ? query : "";
    const response = await window.api.get(window.data_url.issues(projectId, query));
    if (!response.ok) return;
    const issues = await response.json();
    renderIssues(issues);
}

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
        assignee_public_id: publicId,
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
// -----------------------------------------------------------------



// --------- Project Managed ---------------------------------------
async function editProject() {
    const title = prompt("Project title").trim();
    if (title === null) {return;}
    const description = prompt("Description (optional)").trim();
    if (description === null) {return;}
    const res = await api.patch(window.data_url.project(projectId), {name: title, description: description});
    if (!res || !res.ok) {
        alert("Failed to edit project.");
        return;
    }
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

    const response = await window.api.patch(window.data_url.member(projectId, userId), {role: role});
    const data_serv = await response.json();
}

async function delete_member(event) {
    const button = event.target.closest(".remove-btn");
    if (!button) return;
    const userId = button.dataset.userId;
    const response = await window.api.del(window.data_url.member(projectId, userId));
    if (response.status === 204) {
        const member = event.target.closest(".member");
        member.remove();
        member_cnt_obj.textContent = Number(member_cnt_obj.textContent) - 1;
    }
}

async function add_member(event) {
    const btn_add = event.target.closest(".add-btn");

    if (!btn_add) return;
    const user_id = btn_add.dataset.userId;
    const url_members = window.data_url.members(projectId);
    const response = await window.api.post(url_members, {user_public_id: user_id});

    if (!response.ok) {return;}
    const data_serv = await response.json();
    const list_data = [data_serv];
    renderMembers(list_data, ["admin", "member"], true);
    member_cnt_obj.textContent = Number(member_cnt_obj.textContent) + 1;

    user_search.value = "";
    res_search.classList.add("hidden");
    res_search.textContent = "";
    res_search.innerHTML = "";
}

async function user_search(event) {
    const query = event.target.value.trim();
    if (query.length < 2) {
        res_search.classList.add("hidden");
        res_search.innerHTML = "";
        return;
    }
    const response = await window.api.get(window.data_url.searchUsers(query, projectId));

    if (!response.ok) {return;}
    else { res_search.classList.remove("hidden") }
    const users = await response.json();

    let html = "";
    function create_user_text(user) {
        return `<div class="search-item" >
                    <span class="search-user" data-user-id="${user.public_id}">${user.username}</span>
                    <button class="btn-primary add-btn" data-user-id="${user.public_id}">Add</button>
                </div >`
    }
    for (const user of users) {html += create_user_text(user);}
    res_search.innerHTML = html;
}

function manage_members() {modal.classList.toggle("hidden")}

function modal_members(e) { if (e.target === modal) {modal.classList.add("hidden")}}

// ----------------------------------------------------------------


loadProject();