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

const addSorting = document.getElementById("add-sorting");
const sortingMenu = document.getElementById("sorting-menu");
const sortList = document.getElementById("sort-list");

const prjct_created = document.getElementById("project-created");
const project_owner = document.getElementById("project-owner");

const pagination = document.getElementById("pagination");
const count_issues_filtered = document.getElementById("count-issues");
const paginationInfo = document.querySelector(".pagination-info");
const reset_filter = document.getElementById("reset-filters");
const save_filters = document.getElementById("save-filters")
const perPageSelect = document.querySelector("#per-page");


let project_db;
let dragged_button = null;
let dragOffsetX = 0;

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

pagination.addEventListener("click", action_page_pagination);


// --------------------------------------------------------------------


// -----------------------HEAD----------------------------------------
class IssueFilters {
    constructor(projectId) {
        this.key = `issue_filters_${projectId}`;
        this.filters = this.getUrl() ?? this.getLocalStorage();
        this.sortFields = {status: "Status", priority: "Priority", due_date: "Due date"};
        this.appliedFilters = structuredClone(this.filters);
    }

    getUrl() {
        const params = new URLSearchParams(window.location.search);
        if (params.size === 0) {return null;}

        const filters = {};

        for (const [key, value] of params) {
            if (key === "sort") {
                const lastUnderscore = value.lastIndexOf("_");

                const field = value.slice(0, lastUnderscore);
                const direction = value.slice(lastUnderscore + 1);
                (filters.sort ??= []).push({field, direction});
            } else {
                filters[key] = value;
            }
        }

        return filters;
    }

    getLocalStorage() {return JSON.parse(localStorage.getItem(this.key) || "{}");}

    setLocalStorage() {
        const exclude = ["search", "page"];
        const filters = {...this.filters};
        for (const key of exclude) {delete filters[key];}
        if (Object.keys(filters).length === 0) {localStorage.removeItem(this.key)}
        else {localStorage.setItem(this.key, JSON.stringify(filters))}
    }

    change(key, value) {
        let is_empty_list = Array.isArray(value) && value.length === 0;
        let is_empty_value = ["", undefined, null].includes(value);

        if (is_empty_value || is_empty_list) {
            delete this.filters[key];
        } else {
            this.filters[key] = value;
        }

        this.resetPageFilter(key)
        this.updateButtons();
    }

    setUi() {
        issue_search.value = this.filters.search ?? "";
        filterStatus.value = this.filters.status ?? "";
        filterPriority.value = this.filters.priority ?? "";
        filterDueDate.value = this.filters.due_date ?? "";
    }

    setUrl() {
        const params = new URLSearchParams();
        for (const [key, value] of Object.entries(this.filters)) {
            if (key === "sort") {
                value.forEach(item => {params.append("sort", this.serializeSort(item));});
                continue;
            }

            if (value && (key !== "search" || value.length > 1)) {params.set(key, value);}
        }
        const query = params.toString().replaceAll("%5F", "_");
        const url = query ? `${window.location.pathname}?${query}` : window.location.pathname;
        history.replaceState(null, "", url);
    }

    addSort(field) {
        if (!Array.isArray(this.filters.sort)) {this.filters.sort = [];}
        if (this.filters.sort.some(item => item.field === field)) {return;}
        this.filters.sort.push({field, direction: "asc"});
        this.change("sort", this.filters.sort);
    }

    removeSort(field) {
        if (!Array.isArray(this.filters.sort)) {return;}
        this.filters.sort = this.filters.sort.filter(item => item.field !== field);
        this.change("sort", this.filters.sort);
    }

    toggleSort(field) {
        if (!Array.isArray(this.filters.sort)) {return;}
        const sort = this.filters.sort.find(item => item.field === field);
        if (!sort) {return;}
        sort.direction = sort.direction === "asc" ? "desc" : "asc";
        this.change("sort", this.filters.sort);
    }

    resetFilters() {
        const { per_page } = this.filters;
        this.filters = {};
        if (per_page !== undefined) {this.filters.per_page = per_page;}
        this.appliedFilters = structuredClone(this.filters);
        this.setUi();
        this.setLocalStorage();
        this.setUrl();
        this.updateButtons();
    }

    getSortFields() {return this.sortFields}

    getSortValues() {return this.filters.sort || []}

    serializeSort(item) {return `${item.field}_${item.direction}`}

    getListSerializeSort() {
        if (!this.filters.sort?.length) {return [];}
        return this.filters.sort.map(item => this.serializeSort(item));
    }

    getApiFilters() {return {...this.filters, sort: this.getListSerializeSort()}}

    init_filters() {
        this.setUi();
        this.setUrl();
        this.updateButtons();
        renderSort();
    }

    isEqual(a, b) {
        const keys = new Set([...Object.keys(a), ...Object.keys(b)]);

        for (const key of keys) {
            if (["page", "per_page"].includes(key)) {continue;}
            let is_Equal = JSON.stringify(a[key]) !== JSON.stringify(b[key]);
            if (is_Equal) {return false;}
        }

        return true;
    }

    resetPageFilter(key) {
        const resetPageKeys = ["search", "status", "priority", "due_date", "sort", "per_page"];
        if (resetPageKeys.includes(key)) {delete this.filters.page;}
    }

    hasFilters() {return Object.keys(this.filters).some(key => !["page", "per_page"].includes(key));}

    hasChanges() {return !this.isEqual(this.filters, this.appliedFilters);}

    updateButtons() {
        save_filters.disabled = !this.hasChanges();
        reset_filter.disabled = !this.hasFilters();
    }

    apply_save_filters() {
        this.appliedFilters = structuredClone(this.filters);
        this.setLocalStorage();
        this.setUrl();
        this.updateButtons();
    }
}

const issueFilters = new IssueFilters(projectId);

async function loadProject() {
    issueFilters.init_filters();

    const task_project = api.get(window.data_url.project(projectId));
    const task_issue = api.get(window.data_url.issues(projectId, issueFilters.getApiFilters()));

    const [projectRes, issuesRes] = await Promise.all([task_project,task_issue]);

    if (!projectRes?.ok || !issuesRes?.ok) {return;}

    const project = await projectRes.json();
    const issues = await issuesRes.json();

    project_db = {...project,
        members: new Map(project.members.map(member => [member.user.public_id, member])),
        issues: new Map(issues.items.map(issue => [issue.public_id, issue])),
        pagination: {
            total: issues.total,
            filteredTotal: issues.filtered_total,
            page: issues.page,
            perPage: issues.per_page
        }
    };

    const totalPages = Math.ceil(issues.filtered_total / issues.per_page);

    renderDetailProject();
    renderMembers();
    renderIssues(issues.items);

    renderPagination(issues.page, totalPages);
    renderPaginationInfo(issues);
}

const loadIssues = window.debounce(async () => {
    const response = await window.api.get(window.data_url.issues(projectId, issueFilters.getApiFilters()));
    if (!response.ok) return;
    const issues = await response.json();

    project_db.issues = new Map(issues.items.map(issue => [issue.public_id, issue]));
    project_db.pagination = {
        total: issues.total,
        filteredTotal: issues.filtered_total,
        page: issues.page,
        perPage: issues.per_page
    };

    renderIssues(issues.items);
    const totalPages = Math.ceil(issues.filtered_total / issues.per_page);
    renderDetailProject();

    renderPagination(issues.page, totalPages);
    renderPaginationInfo(issues);
})

issue_search.addEventListener("input", () => {
    const value = issue_search.value.trim();
    const search = value.length > 1 ? value : "";
    issueFilters.change("search", search)
    if (value.length === 1) {return;}
    loadIssues();
    issueFilters.setUrl();
});

function changeFilter(key, value) {issueFilters.change(key, value)}
filterStatus.addEventListener("change", () => changeFilter("status", filterStatus.value));
filterPriority.addEventListener("change", () => changeFilter("priority", filterPriority.value));
filterDueDate.addEventListener("change", () => changeFilter("due_date", filterDueDate.value));

function create_span(cls, str){return `<span class="${cls}">${str}</span>`;}
// --------------------------------------------------------------------


// ----------------------------SORT------------------------------------
function except_field_add_sort(event) {
    const button = event.target.closest("[data-sort]");
    if (!button) {return;}

    const field = button.dataset.sort;

    sortingMenu.classList.add("hidden");

    issueFilters.addSort(field);
    renderSort();
}

function renderSort() {
    sortList.innerHTML = "";
    let html = "";
    issueFilters.getSortValues().forEach(sort => {html += create_filter_element(sort)});
    sortList.innerHTML = html;

    addSorting.hidden = issueFilters.getSortValues().length > 2;

    const list_buttons_sort = sortList.querySelectorAll(".sort-item");
    list_buttons_sort.forEach(element => {
        element.addEventListener("click", click_action_sort);

        const handle = element.querySelector(".drag-drop");

        handle.draggable = true;

        handle.addEventListener("dragstart", drag_start);
        handle.addEventListener("dragend", drag_end);
    });

    const selected = issueFilters.getSortValues().map(item => item.field);

    sortingMenu.querySelectorAll("[data-sort]").forEach(button => {
        if (selected.includes(button.dataset.sort)) {
            button.classList.add("hidden");
        } else {
            button.classList.remove("hidden");
        }
    });

    function create_filter_element(sort) {
        return `<button class="sort-item" type="button" data-field="${sort.field}">
                    ${create_span("drag-drop", "☷")}
                    ${create_span("value", issueFilters.getSortFields()[sort.field])}
                    ${create_span("direction", sort.direction === "asc" ? "↑" : "↓")}
                    ${create_span("sort-remove", "×")}
                </button>`;
    }
}

function click_action_sort(event) {
    const button = event.currentTarget;
    const field = button.dataset.field;

    if (event.target.classList.contains("sort-remove")) {issueFilters.removeSort(field);renderSort();}
    else if (!event.target.classList.contains("drag-drop")) {issueFilters.toggleSort(field);renderSort();}
}

function updateSortOrder() {
    const fields = [...sortList.querySelectorAll(".sort-item")].map(element => element.dataset.field);
    const list_sort = issueFilters.getSortValues()
    list_sort.sort((a, b) => {return fields.indexOf(a.field) - fields.indexOf(b.field);});
    issueFilters.change("sort",list_sort);
}

function drag_start(event) {
    dragged_button = event.currentTarget.closest(".sort-item");
    dragged_button.classList.add("dragging");
    const rect = dragged_button.getBoundingClientRect();
    dragOffsetX = event.clientX - rect.left;
    const offsetY = event.clientY - rect.top;
    event.dataTransfer.setDragImage(dragged_button, dragOffsetX, offsetY);
    event.dataTransfer.effectAllowed = "move";
}

function drag_end() {
    if (!dragged_button) {return;}
    dragged_button.classList.remove("dragging");
    dragged_button = null;
}

function drag_over(event) {
    event.preventDefault();
    if (!dragged_button) {return;}

    const ghostCenterX = event.clientX - dragOffsetX + dragged_button.offsetWidth / 2;

    const items = [...sortList.querySelectorAll(".sort-item")];

    const draggedIndex = items.indexOf(dragged_button);
    if (draggedIndex === -1) {return;}

    // Тащим вправо
    if (draggedIndex < items.length - 1) {
        const next = items[draggedIndex + 1];
        const rect = next.getBoundingClientRect();
        if (ghostCenterX >= rect.left) {sortList.insertBefore(dragged_button, next.nextSibling);return;}
    }

    // Тащим влево
    if (draggedIndex > 0) {
        const prev = items[draggedIndex - 1];
        const rect = prev.getBoundingClientRect();

        if (ghostCenterX <= rect.right) {sortList.insertBefore(dragged_button, prev);}
    }
}

function drop(event) {
    event.preventDefault();
    if (!dragged_button) {return;}
    updateSortOrder();
}

function reset_sort_filters(event) {issueFilters.resetFilters(); loadIssues(); renderSort();}

function save_filters_and_reload(event) {loadIssues();issueFilters.apply_save_filters();}

function per_page_change(event) {
    issueFilters.change("per_page", Number(perPageSelect.value));
    issueFilters.setLocalStorage();
    issueFilters.setUrl();
    loadIssues();
}


reset_filter.addEventListener("click", reset_sort_filters);
save_filters.addEventListener("click", save_filters_and_reload);
document.addEventListener("dragover", drag_over);
document.addEventListener("drop", drop);
addSorting.addEventListener("click", () => {sortingMenu.classList.toggle("hidden");});
sortingMenu.addEventListener("click", except_field_add_sort);
perPageSelect.addEventListener("change", per_page_change);
// --------------------------------------------------------------------


// -------------------------RENDER_UI----------------------------------
function renderDetailProject() {
    title.textContent = project_db.name;
    description.textContent = project_db.description || "No description";
    member_cnt_obj.textContent = project_db.members.size;
    issues_cnt_obj.textContent = project_db.pagination.total;
    prjct_created.textContent =  window.formatDate(project_db.created_at, 4);
    project_owner.textContent = project_db.owner.username;
    count_issues_filtered.textContent = `(${project_db.pagination.filteredTotal})`;
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
    const isOverdue = issue =>  issue.due_date && new Date(issue.due_date) < new Date() && issue.status !== "done";

    for (const issue of issues) {html += issue_text(issue);}

    issuesContainer.innerHTML = html;

    function formatEnum(value) {
        return value
            .replaceAll("_", " ")
            .replace(/\b\w/g, c => c.toUpperCase());
    }

    function issue_text(issue) {
      const is_overdue =  isOverdue(issue);
      const assignee = issue.assignee?.username ?? "Unassigned";
      return `<a href="/projects/${projectId}/issues/${issue.public_id}" data-id="${issue.public_id}" class="issue">
                <div>
                    <h3>${issue.title}</h3>
                    ${create_span("assignee-name",`Assigned to ${assignee} • Reported by ${issue.reporter.username}`)}
                </div>
                <div class="badges">
                    ${create_span(is_overdue? "overdue due" :"due",window.formatDate(issue.due_date, 0, true))}
                    ${is_overdue? create_span("issue-overdue", "Overdue"): ""}
                    ${create_span(issue.priority.toLowerCase(),issue.priority.toUpperCase())}
                    ${create_span(issue.status,formatEnum(issue.status.toUpperCase()))}
                </div>
            </a>`
    }
}

function renderPagination(currentPage, totalPages) {
    pagination.innerHTML = "";

    const pages = getPages(currentPage, totalPages);

    pages.forEach(page => {
        if (page === "...") {
            pagination.insertAdjacentHTML("beforeend", `<span class="pagination-dots">...</span>`);
            return;
        }

        const cls = page === currentPage ? "active" : "";

        pagination.insertAdjacentHTML(
            "beforeend", `<button type="button" class="${cls}" data-page="${page}" >${page}</button>`
        );
    });

    function getPages(currentPage, totalPages) {
        if (totalPages <= 7) {return Array.from({length: totalPages}, (_, i) => i + 1);}
        const pages = [];

        pages.push(1);

        if (currentPage > 4) {pages.push("...");}

        const start = Math.max(2, currentPage - 2);
        const end = Math.min(totalPages - 1, currentPage + 2);

        for (let page = start; page <= end; page++) {pages.push(page);}

        if (currentPage < totalPages - 3) {pages.push("...");}
        pages.push(totalPages);

        return pages;
    }
}

function action_page_pagination(event) {
    const button = event.target.closest("[data-page]");
    if (!button) {return;}
    const page = Number(button.dataset.page);
    if (!page) {return;}
    issueFilters.change("page", page);
    loadIssues();
    issueFilters.setUrl();
}

function renderPaginationInfo(issues) {
    const {page, per_page, filtered_total} = issues;

    perPageSelect.value = per_page;

    if (filtered_total === 0) {
        paginationInfo.textContent = "No issues";
        return;
    }

    const start = (page - 1) * per_page + 1;
    const end = Math.min(page * per_page, filtered_total);

    paginationInfo.textContent = `Showing ${start}–${end} of ${filtered_total} issues`;
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
    loadIssues();
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

function manage_members() {modal.classList.toggle("hidden")}

function modal_members(e) { if (e.target === modal) {modal.classList.add("hidden")}}

user_search_input.addEventListener('input', user_search_func);
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
        loadIssues();
        renderDetailProject();
    }

    function issue_delete(event) {
        // project_db.issues.delete(event.payload.issue.public_id);
        // renderIssues([...project_db.issues.values()]);
        // renderDetailProject();
        loadIssues();
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
        // const data = event.payload;
        // const issue = project_db.issues.get(data.issue.public_id);
        // issue.status = data.new_value;
        // renderIssues([...project_db.issues.values()]);
        loadIssues();
        renderDetailProject();
    }

    function issue_priority_change(event) {
        // const data = event.payload;
        // const issue = project_db.issues.get(data.issue.public_id);
        // issue.priority = data.new_value;
        // renderIssues([...project_db.issues.values()]);
        loadIssues();
        renderDetailProject();
    }

    function issue_due_date_change(event) {
        // const data = event.payload;
        // const issue = project_db.issues.get(data.issue.public_id);
        // issue.due_date = data.new_value;
        // renderIssues([...project_db.issues.values()]);
        loadIssues();
        renderDetailProject();
    }

    function issue_closed(event) {
        loadIssues();
        renderDetailProject();
    }

    function issue_reopen(event) {
        loadIssues();
        renderDetailProject();
    }
}

window.appEvents.on("*", (event) => {
    const handler = all_project_event;
    if (handler) {handler(event);}
});
// ----------------------------------------------------------------

loadProject();