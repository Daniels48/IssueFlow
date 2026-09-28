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

// --------- Event Managed -----------------------------------------
edit_btn.addEventListener("click", editProject);
del_btn.addEventListener("click", deleteProject);
manage_btn.addEventListener("click", manage_members);
modal_close_btn.addEventListener("click", manage_members);
modal.addEventListener("click", modal_members);

membersContainer.addEventListener("click", delete_member);
res_search.addEventListener("click", add_member)
membersContainer.addEventListener("change", change_role);
issue_new_btn.addEventListener("click", view_new_issue_modal);
close_issue_modal.addEventListener("click", closeIssueModal);
form_issue.addEventListener("submit", createIssue);
cancel_issue_form.addEventListener("click", clear_new_issue_form);
modal_issue.addEventListener("click", handleIssueModalBackdropClick);

const issueFilters = new IssueFilters(projectId);

// -----------------------HEAD----------------------------------------
async function loadProject() {
    issueFilters.setUi();
    issueFilters.setUrl();

    const task_project = api.get(window.data_url.project(projectId));
    const task_issue = api.get(window.data_url.issues(projectId, issueFilters.get()));

    const [projectRes, issuesRes] = await Promise.all([task_project,task_issue]);

    if (!projectRes?.ok || !issuesRes?.ok) {return;}

    const project = await projectRes.json();
    const issues = await issuesRes.json();

    project_db = {...project,
        members: new Map(project.members.map(member => [member.user.public_id, member])),
        issues: new Map(issues.map(issue => [issue.public_id, issue]))
    };

    renderDetailProject();
    renderMembers();
    renderIssues(issues);
}

const loadIssues = window.debounce(async () => {
    const search = issue_search.value.trim();
    issueFilters.changeSearch(search.length >= 2 ? search : "");
    issueFilters.setUrl()

    const response = await window.api.get(window.data_url.issues(projectId, issueFilters.get()));
    if (!response.ok) return;
    const issues = await response.json();
    renderIssues(issues);
})

class IssueFilters {
    constructor(projectId) {
        this.key = `issue_filters_${projectId}`;
        this.filters = this.getUrl() ?? this.getLocalStorage();
    }

    getUrl() {
        const params = new URLSearchParams(window.location.search);
        if (params.size === 0) {return null;}
        return Object.fromEntries(params.entries());
    }

    getLocalStorage() {return JSON.parse(localStorage.getItem(this.key) || "{}");}

    setLocalStorage() {localStorage.setItem(this.key, JSON.stringify(this.filters));}

    setUrl() {
        const params = new URLSearchParams();
        for (const [key, value] of Object.entries(this.filters)) {
            if (value && (key !== "search" || value.length >= 2)) {params.set(key, value);}
        }
        const query = params.toString();
        const url = query ? `${window.location.pathname}?${query}` : window.location.pathname;
        history.replaceState(null, "", url);
    }

    setUi() {
        issue_search.value = this.filters.search ?? "";
        filterStatus.value = this.filters.status ?? "";
        filterPriority.value = this.filters.priority ?? "";
        filterDueDate.value = this.filters.due_date ?? "";
        sortIssues.value = this.filters.sort ?? "";
    }

    change(key, value) {
        this.filters[key] = value;
        this.setLocalStorage();
    }

    changeSearch(value) {this.filters.search = value;}

    get() {return this.filters;}
}

function changeFilter(key, value) {issueFilters.change(key, value);loadIssues();}

issue_search.addEventListener("input", loadIssues);

filterStatus.addEventListener("change", () => changeFilter("status", filterStatus.value));
filterPriority.addEventListener("change", () => changeFilter("priority", filterPriority.value));
filterDueDate.addEventListener("change", () => changeFilter("due_date", filterDueDate.value));
sortIssues.addEventListener("change", () => changeFilter("sort", sortIssues.value));
// -------------------------------------------------------------------


// -------------------------RENDER_UI----------------------------------
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
    if (members.length === 0) {membersContainer.innerHTML = `<div class="empty">No members</div>`;return;}

    let html = "";
    for (const member of members) {html += member_text(member)}
    membersContainer.innerHTML = html;
    issue_assignee.innerHTML = set_members_issue_new(members);

    function member_text(member) {
        const data_id = `data-user-id="${member.user.public_id}"`

        let text = `<select class="role-select" ${data_id}>${get_option(member)}</select>
                          <button class="remove-btn" ${data_id}>Remove</button>`;

        if (project_db.owner.public_id === member.user.public_id) {text = `<span class="owner-badge">Owner</span>`}

        return `<div class="member">
                    <div class="member-info">
                        <span class="member-name">${member.user.username}</span>
                    </div>
                    <div class="member-actions">${text}</div>
                </div>`;
    }

    function get_option(member) {
        let options = "";
        const capitalize = text => text.charAt(0) + text.slice(1).toLowerCase();
        const is_selected = (member, role) => member.role === role ? "selected" : ""
        const get_option = role => `<option value="${role}" ${is_selected(member, role)}>${capitalize(role)}</option>`
        for (const role of roles) {options += get_option(role)}
        return options;
    }

    function set_members_issue_new(members) {
        let html =  `<option value="" selected disabled>Choose member</option>`;
        const member_text = member => `<option data-id="${member.user.public_id}">${member.user.username}</option>`
        for (const member of members) {html += member_text(member);}
        return html;
    }
}

function renderIssues(issues) {
    if (issues.length === 0) {issuesContainer.innerHTML = `<div class="empty">No issues</div>`;return;}
    let html = "";
    for (const issue of issues) {html += issue_text(issue);}
    issuesContainer.innerHTML = html;

    function issue_text(issue) {
      const assignee = issue.assignee?.username ?? "Unassigned";
      const create_span = (cls, str) => `<span class="${cls}">${str}</span>`;
      return `<a href="/projects/${projectId}/issues/${issue.public_id}" data-id="${issue.public_id}" class="issue">
                <div>
                    <h3>${issue.title}</h3>
                    ${create_span("assignee-name",`Assigned to ${assignee} • Reported by ${issue.reporter.username}`)}
                </div>
                <div class="badges">
                    ${create_span("due",window.formatDate(issue.due_date))}
                    ${create_span("progress",issue.status.toUpperCase())}
                    ${create_span(issue.priority.toLowerCase(),issue.priority.toUpperCase())}
                </div>
            </a>`
    }
}
// --------------------------------------------------------------------


// --------- Issue Managed -----------------------------------------

async function createIssue(event) {
    event.preventDefault();

    const data = {
        title: document.getElementById("issue-title").value,
        description: document.getElementById("issue-description").value || null,
        assignee_id: issue_assignee.selectedOptions[0]?.dataset.id ?? null,
        priority: document.getElementById("issue-priority").value,
        due_date: window.toUTC(document.getElementById("issue-date").value),
    };

    const response = await window.api.post(window.data_url.issues(projectId), data);
    if (!response.ok) {return}
    const new_issue = await response.json();
    project_db.issues.set(new_issue.public_id, new_issue);
    renderDetailProject();
    renderIssues([...project_db.issues.values()]);
    closeIssueModal();
}

function view_new_issue_modal(event) {modal_issue.classList.remove("hidden")}

function closeIssueModal(event) {modal_issue.classList.add("hidden");form_issue.reset()}

function handleIssueModalBackdropClick(event) {if (event.target === modal_issue) {closeIssueModal()}}

function clear_new_issue_form(event) {event.preventDefault();form_issue.reset();}
// --------------------------------------------------------------------


// --------- Project Managed ---------------------------------------
async function editProject() {
    const titleInput = prompt("Project title");
    if (titleInput === null) {return;}
    const title = titleInput.trim();
    const description = prompt("Description (optional)")?.trim() ?? "";
    const data = {name: title, description: description};
    const res = await api.patch(window.data_url.project(projectId), data);
    if (!res || !res.ok) {alert("Failed to edit project.");return;}
    const data_res = await res.json()
    Object.assign(project_db, data_res);
    renderDetailProject();
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

const user_search_func = window.debounce(async (event) => {
    const query = event.target.value.trim();
    if (query.length < 2) {updateSearchResults("clear");return}
    const response = await window.api.get(window.data_url.searchUsers(query, projectId));
    if (!response.ok) {updateSearchResults("clear");return}
    const users = await response.json();
    if (!users) {updateSearchResults("clear");return}
    let html = "";
    for (const user of users) {html += create_user_text(user);}
    updateSearchResults("render", html);
    updateSearchResults("show");

    function create_user_text(user) {
        return `<div class="search-item" >
                    <span class="search-user" data-user-id="${user.public_id}">${user.username}</span>
                    <button class="btn-primary add-btn" data-user-id="${user.public_id}">Add</button>
                </div >`
    }
})

user_search_input.addEventListener('input', user_search_func);

function manage_members() {modal.classList.toggle("hidden")}

function modal_members(e) { if (e.target === modal) {modal.classList.add("hidden")}}
// ----------------------------------------------------------------



// ---------------------------WS------------------------------------
function all_project_event(event) {
    const handlers = {
        "project.updated": update_project,
        "project.deleted": delete_project,

        "project.member.added": member_add,
        "project.member.removed": member_delete,
        "project.member.role.changed": member_change,

        "issue.created": issue_new,
        "issue.updated": issue_update,
        "issue.deleted": issue_delete,

        "issue.assigned": issue_assigned,
        "issue.unassigned": issue_unassigned,

        "issue.status.changed": issue_status_change,
        "issue.priority.changed": issue_priority_change,
        "issue.due_date.changed": issue_due_date_change,

        "issue.closed": issue_closed,
        "issue.reopened": issue_reopen,

    };
    console.log(event);
    const handler = handlers[event.event_type];
    if (handler) {handler(event);}

    function create_member_data(data) {
        return {
            user: {
                public_id: data.user.public_id,
                username: data.user.username,
            },
            role: data.member.role,
        }
    }

    function update_project(event) {
        Object.assign(project_db, {...event.payload.project, updated_at: event.payload.occurred_at});
        renderDetailProject();
    }

    function delete_project(event) {
        const data = event.payload;
        window.location.href = "/projects";
        // ????
    }

    function member_add(event) {
        const data = event.payload;
        const new_member = create_member_data(data)
        project_db.members.set(new_member.user.public_id, new_member);
        renderMembers();
        renderDetailProject();
        /////////////////////
    }

    function member_delete(event) {
        const data = event.payload;
        project_db.members.delete(data.user.public_id);
        renderMembers();
        renderDetailProject();
        /////
    }

    function member_change(event) {
        const data = event.payload;
        const new_member = create_member_data(data)
        project_db.members.set(new_member.user.public_id, new_member);
        renderMembers();
        renderDetailProject();
        /////////////////////
    }

    function issue_new(event) {
        const data = event.payload;
        const new_issue = {
            ...data.issue,
            status: "open",
            reporter: {
                username: data.author.username,
                public_id: data.author.public_id
            }
        };
        project_db.issues.set(new_issue.public_id, new_issue);
        renderIssues([...project_db.issues.values()]);
        renderDetailProject();
    }

    function issue_delete(event) {
        project_db.issues.delete(event.payload.issue.public_id);
        renderIssues([...project_db.issues.values()]);
        renderDetailProject();
    }

    function issue_update(event) {
        const data = event.payload;
        const issue = project_db.issues.get(data.issue.public_id);
        Object.assign(issue, data.issue);
        renderIssues([...project_db.issues.values()]);
    }

    function issue_assigned(event) {
        const data = event.payload;
        const issue = project_db.issues.get(data.issue.public_id);
        const { public_id, username } = data.new_value;
        issue.assignee = {public_id, username};
        renderIssues([...project_db.issues.values()]);
    }

    function issue_unassigned(event) {
        const data = event.payload;
        const issue = project_db.issues.get(data.issue.public_id);
        issue.assignee = null;
        renderIssues([...project_db.issues.values()]);
    }

    function issue_status_change(event) {
        const data = event.payload;
        const issue = project_db.issues.get(data.issue.public_id);
        issue.status = data.new_value;
        renderIssues([...project_db.issues.values()]);
    }

    function issue_priority_change(event) {
        const data = event.payload;
        const issue = project_db.issues.get(data.issue.public_id);
        issue.priority = data.new_value;
        renderIssues([...project_db.issues.values()]);
    }

    function issue_due_date_change(event) {
        const data = event.payload;
        const issue = project_db.issues.get(data.issue.public_id);
        issue.due_date = data.new_value;
        renderIssues([...project_db.issues.values()]);
    }

    function issue_closed(event) {

    }

    function issue_reopen(event) {

    }
}

window.appEvents.on("*", (event) => {
    const handler = all_project_event;
    if (handler) {handler(event);}
});
// ----------------------------------------------------------------

loadProject();