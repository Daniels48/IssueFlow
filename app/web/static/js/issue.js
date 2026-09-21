const path = window.location.pathname.split("/");
const projectId = path.at(-3);
const IssueId = path.at(-1);


const back_url = document.getElementById("back");
// ----------------------------Issue Detail----------------------------------------
const status = document.getElementById("status");
const priority = document.getElementById("priority");
const reporter = document.getElementById("reporter");
const assignee = document.getElementById("assignee");
const due_time = document.getElementById("due_time");
const created_time = document.getElementById("created_time");
const updated_time = document.getElementById("updated_time");
const title = document.getElementById("title");
const head_status = document.getElementById("head_status");
const head_priority = document.getElementById("head_priority");
const description = document.getElementById("description");
const len_comments = document.getElementById("len-comments");
// --------------------------------------------------------------------------------


const btn_post_comment = document.getElementById("post_comment");

// ------------------------------------------------------------------------------
const text_area_comment = document.getElementById("text_area");
const commentsContainer = document.getElementById("comments");
const modal_issue = document.getElementById("issue-modal");
const btn_edit_issue = document.getElementById("edit-issue");
const btn_issue_action = document.getElementById("issue-action");
const close_issue_modal = document.getElementById("modal-close");
const form_issue = document.getElementById("issue-form");
const cancel_issue_form = document.getElementById("cancel_issue_form");
// ------------------------------------------------------------------------------


// ------------------------------------------------------------------------------
const i_title= document.getElementById("issue-title")
const i_description = document.getElementById("issue-description")
const i_assignee= document.getElementById("issue-assignee");
const i_priority = document.getElementById("issue-priority");
const i_due_date =document.getElementById("issue-date");
const i_status = document.getElementById("issue-status");
const i_apply = document.getElementById("update_btn");
// ------------------------------------------------------------------------------


const replyInfo = document.getElementById("reply-info");
const replyAuthor = document.getElementById("reply-author");
const replyPreview = document.getElementById("reply-preview");

const cancelReply = document.getElementById("cancel-reply");

// const postComment = document.getElementById("post_comment");
// const textArea = document.getElementById("text_area");


const fieldModal = document.querySelector("#field-modal");
const fieldModalTitle = document.querySelector("#field-modal-title");
const fieldModalBody = document.querySelector("#field-modal-body");

const fieldModalClose = document.querySelector("#field-modal-close");
const fieldModalCancel = document.querySelector("#field-modal-cancel");
const fieldModalSave = document.querySelector("#field-modal-save");


btn_edit_issue.addEventListener("click", OpenEditIssueWindow);
btn_issue_action.addEventListener("click", issue_action)
close_issue_modal.addEventListener("click", close_issue_edit_window);
cancel_issue_form.addEventListener("click", reset_issue_form);
modal_issue.addEventListener("click", modal_issue_func);
i_apply.addEventListener("click", applyEditTitle_and_Description);
commentsContainer.addEventListener("click", comments_action);
cancelReply.addEventListener("click", cancel_reply_comment);
btn_post_comment.addEventListener("click", post_comment);

back_url.href = back_url.href + projectId;

let issue_full = false;
let issue_statuses = false;
let issue_priority = false;
let issue_assignee = false;
let issue_comments = false



// ---------------------------------------Head----------------------------------------------
function change_UI_status_issue(issue) {
    head_status.textContent = formatEnum(issue.status).toUpperCase();
    status.textContent = formatEnum(issue.status).toUpperCase();
    const get_action = (element) => element.status === "closed" ? "reopen" : "close";
    const value = get_action(issue);
    btn_issue_action.dataset.action = value;
    btn_issue_action.textContent = value.charAt(0).toUpperCase() + value.slice(1).toLowerCase()
    issue_statuses = issue.allowed_statuses

    setCommentActionsVisibility(issue.status);
    drawCommentLines();
}

function change_UI_title_and_description(issue) {
    title.textContent = issue.title;
    description.textContent = issue.description;
}

function change_UI_due_time(issue) {
    due_time.textContent = issue.due_date ? window.formatDate(issue.due_date, 0, true) : "No due date";
    due_time.dataset.value = issue.due_date || "";
}

function change_UI_priority(issue) {
    priority.textContent = issue.priority.toUpperCase();
    head_priority.textContent = issue.priority.toUpperCase();
}

function change_UI_assignee(issue) {
    assignee.textContent = issue.assignee?.username ?? "Unassigned";
    assignee.dataset.publicId = issue.assignee?.public_id ?? "";
}

function change_UI_updated_time(issue) {
    updated_time.textContent = window.relativeDate(issue.updated_at);
}

function setCommentActionsVisibility(value) {
    const action = value === "closed" ? "add" : "remove";
    const cls = "hidden";

    document.querySelectorAll(".comment-actions").forEach(element => element.classList[action](cls));
    document.querySelectorAll("span.arrow").forEach(element => element.classList[action](cls))
    document.querySelector("section.new-comment").classList[action](cls);
    document.querySelector("#edit-issue").classList[action](cls)
}

async function loadIssue() {
    const res = await api.get(window.data_url.issue(projectId, IssueId));
    if (!res || !res.ok) {
        return;
    }
    const Issue = await res.json();
    renderIssueDetails(Issue, true);
    renderComments(Issue.comments);
    issue_full = Issue;
    issue_assignee = Issue.members;
    issue_priority = Issue.priorities;
    issue_statuses = Issue.allowed_statuses;
    issue_comments = Issue.comments;

    setCommentActionsVisibility(Issue.status)
    drawCommentLines()
}

function renderIssueDetails(issue, offload=false) {
    reporter.textContent = issue.reporter.username;
    created_time.textContent = window.formatDate(issue.created_at, 4);

    change_UI_updated_time(issue)
    change_UI_assignee(issue)
    change_UI_priority(issue)
    change_UI_due_time(issue)
    change_UI_title_and_description(issue)
    change_UI_status_issue(issue)

    if (offload !== false) {
        const count = countComments(issue.comments);
        set_count_comments(count);
    }


    function countComments(comments) {
        return comments.reduce((count, comment) => {
            return count + 1 + countComments(comment.children);
        }, 0);
    }
}

function addTextNoComments() {
    const empty_text = `<div class="empty">No comments</div>`;
    commentsContainer.insertAdjacentHTML("beforeend", empty_text);
}

function renderComments(comments) {
    if (comments.length === 0) {
        addTextNoComments()
        return;
    }

    commentsContainer.insertAdjacentHTML("beforeend", renderTree(comments));
    drawCommentLines()

    function renderTree(comments, level = 0, parent = null) {
        let html = ``;
        for (const comment of comments) {
            html += commentHtml(comment, level, parent);
            if (comment.children.length) {html += renderTree(comment.children, level + 1, comment)}
        }
        return html;
    }
}

function commentHtml(comment, level, parent) {
    const visualLevel = Math.min(level, 8);

    function getChildrenAttribute(comment) {
        if (!comment.children?.length) return "";

        const ids = [];

        function walk(node) {
            for (const child of node.children) {
                ids.push(child.public_id);
                walk(child);
            }
        }

        walk(comment);

        return `data-list-ids='${JSON.stringify(ids)}'`;
    }

    const set_parent_id = parent => parent ? `data-parent="${parent.public_id}"` : "";

    function commentReply(parent, is_par=true) {
        if (is_par) return "";
        return `<div class="reply-preview">
                    <span>Replying to ${parent.author.username}</span>
                    <blockquote>${parent.content}</blockquote>
                </div>`;
    }

    function getUpdateTime(comment) {
        if (!comment.updated_at) return "";
        const isEdited = Math.abs(new Date(comment.updated_at) - new Date(comment.created_at)) > 1000;
        return isEdited ? window.relativeDate(comment.updated_at, "edited") : window.relativeDate(comment.created_at);
    }

    function setArticleAttributes(parent, comment, visualLevel) {
        return`
        ${set_parent_id(parent)} ${getChildrenAttribute(comment)} 
        data-id="${comment.public_id}" class="comment level-${visualLevel} card2"`
    }

    let z = `<button class="toggle-replies">▼ 4 replies</button>`

    return `
    <article ${setArticleAttributes(parent, comment, visualLevel)}>
            <div class="avatar">${comment.author.username.charAt(0).toUpperCase() || ""}</div>
            <div class="comment-content">
                <div class="comment-header">
                    <strong class="comment-owner" data-owner="${comment.author.username}">@${comment.author.username}</strong>
                    <span class="comment-create-date">${getUpdateTime(comment)}</span>
                </div>
                
                ${parent ? commentReply(parent) : ""}
                
                <div class="comment-head">
                    <p class="content-comment" data-text="${comment.content}">${comment.content}</p>
                    <div class="comment-actions">
                        <button class="btn_reply">Reply</button>
                        <button class="btn_edit">Edit</button>
                        <button class="btn_delete">Delete</button>
                    </div>
                </div>
                
                <div class="comment-edit hidden">
                    <textarea class="comment-area">${comment.content}</textarea>
                    <div class="edit-actions">
                        <button class="btn-save">Save</button>
                        <button class="btn-cancel">Cancel</button>
                    </div>
                </div>
                
            </div>
        </article>`;
}

function drawCommentLines() {
    const svg = document.querySelector("#comment-lines");
    svg.innerHTML = "";

    const comments = commentsContainer.querySelectorAll(".comment");

    for (const child of comments) {
        const rects = getCommentRects(child);

        if (!rects) continue;

        const coords = getCommentLineCoordinates(rects.parentRect, rects.childRect, svg.getBoundingClientRect())
        const path = createCommentLine(coords)
        svg.appendChild(path);
    }


    function getCommentRects(child) {
        const parentId = child.dataset.parent;

        if (!parentId) return null;

        const parent = findCommentElement(parentId);

        if (!parent) return null;

        const parentAvatar = parent.querySelector(".avatar");
        const childAvatar = child.querySelector(".avatar");

        if (!parentAvatar || !childAvatar) return null;

        return {
            parentRect: parentAvatar.getBoundingClientRect(),
            childRect: childAvatar.getBoundingClientRect()
        };
    }

    function getCommentLineCoordinates(parentRect, childRect, svgRect, gap=10) {
        const x1 = parentRect.left + parentRect.width / 2 - svgRect.left;
        const y1 = parentRect.bottom - svgRect.top;

        const x2 = childRect.left - svgRect.left - gap;
        const y2 = childRect.top + childRect.height / 2 - svgRect.top;

        return {x1: x1, y1: y1, x2: x2, y2: y2}
    }

    function createCommentLine(coords) {
            const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
            path.setAttribute("d", `
                M ${coords.x1} ${coords.y1}
                V ${coords.y2}
                H ${coords.x2}`
            );

            path.setAttribute("fill", "none");
            path.setAttribute("stroke", "#64748b");
            path.setAttribute("stroke-width", "1");
            path.setAttribute("stroke-linecap", "round");
            path.setAttribute("stroke-linejoin", "round");
            path.setAttribute("opacity", "0.5");

            return path;
    }
}

const set_count_comments = count => len_comments.textContent = `${count} comment${count === 1 ? "" : "s"}`;
// -----------------------------------------------------------------------------------------




// ------------------------------------Comments Action--------------------------------------
async function comments_action(event) {
    const btn = event.target;
    const container = btn.closest("article.comment");
    if (!container) {return;}
    const obj_comment = container.querySelector("p.content-comment");
    const owner_comment = container.querySelector("strong.comment-owner");

    const data = {
        id: container.dataset.id,
        value: obj_comment.dataset.text,
        owner: owner_comment.dataset.owner,
        container: container,
        textarea: container.querySelector(".comment-area"),
    }

    if (btn.classList.contains("btn_reply")) {reply_comment(data);}
    if (btn.classList.contains("btn_edit")) {edit_comment(data);}
    if (btn.classList.contains("btn_delete")) {await delete_comment(data);}
    if (btn.classList.contains("btn-cancel")) {close_edit_comment(data);}
    if (btn.classList.contains("btn-save")) {await save_edit_comment(data);}

}

function get_containers_edit(data) {
    return {
        head_container: data.container.querySelector(".comment-head"),
        edit_container: data.container.querySelector(".comment-edit")
    }
}

function edit_comment(data) {
    const containers = get_containers_edit(data);
    containers.head_container.classList.add("hidden");
    containers.edit_container.classList.remove("hidden");

    const textarea = data.container.querySelector("textarea.comment-area");
    textarea.value = data.value;
    textarea.focus();
    textarea.setSelectionRange(textarea.value.length, textarea.value.length);
}

function close_edit_comment(data) {
    const containers = get_containers_edit(data);
    containers.head_container.classList.remove("hidden");
    containers.edit_container.classList.add("hidden");
}

async function save_edit_comment(data) {
    const dict = {
        content: data.textarea.value,
    }
    const res = await api.patch(window.data_url.comments(projectId, IssueId, data.id), dict);
    if (!res || !res.ok) {return;}
    else {
        alert("Comment success update!")
        const comment = await res.json();
        const edit_string = data.container.querySelector(".comment-meta");
        edit_string.textContent = window.relativeDate(comment.updated_at, "edited");
        close_edit_comment(data);
        const obj_comment = data.container.querySelector("p.content-comment");
        obj_comment.dataset.text = comment.content;
        obj_comment.textContent = comment.content;
        const id_comment = data.id;
        if (id_comment) {
            const elements = document.querySelectorAll(`[data-parent="${id_comment}"]`);
            if (elements.length) {
                for (const element of elements) {
                    let container_element = element.querySelector("blockquote")
                    container_element.textContent = comment.content;
                }
            }
        }
    }
}

function reply_comment(data) {
    replyAuthor.textContent = data.owner;
    replyPreview.textContent = data.value;
    text_area_comment.dataset.id = data.id;
    replyInfo.classList.remove("hidden");
    text_area_comment.focus();
}

function cancel_reply_comment() {
    replyInfo.classList.add("hidden");
    replyAuthor.textContent = "";
    replyPreview.textContent = "";
    delete text_area_comment.dataset.id;
}

function findCommentElement(id) {
    return commentsContainer.querySelector(`[data-id="${id}"]`);
}

function delete_comment_in_ui(id) {
    const element = findCommentElement(id)
    if (!element) {return}

    const listIds = JSON.parse(element.dataset.listIds || "[]");
    for (const childId of listIds) {findCommentElement(childId)?.remove()}

    const idsToRemove = [...new Set([...listIds, id])];
    updateChildIdsInParents(element, idsToRemove, "-")
    deleteComment_in_js(issue_comments, id)

    element.remove();
    const count = commentsContainer.children.length - 1;
    set_count_comments(count);
    if (count === 0) {addTextNoComments()}
    drawCommentLines()

    function deleteComment_in_js(comments, id) {
        for (let i = 0; i < comments.length; i++) {
            if (comments[i].public_id === id) {
                comments.splice(i, 1);
                return true;
            }
            if (deleteComment_in_js(comments[i].children || [], id)) {return true}
        }
        return false;
    }
}

function add_comment_in_ui(comment) {
    const count = parseInt(len_comments.textContent, 10);

    if (count === 0) {
        const empty = commentsContainer.querySelector("div.empty")
        if (empty) {empty.remove()}
    }

    let added;

    if (comment.parent_comment_public_id) {added = addReplyComment(comment)}
    else {added = addNewComment(comment);}

    if (!added) return;

    set_count_comments(count + 1);
    drawCommentLines()

    function addReplyComment(comment) {
        const parentElement = findCommentElement(comment.parent_comment_public_id)
        if (!parentElement) return;

        const parent = findComment(issue_comments, comment.parent_comment_public_id)
        if (!parent) return false;
        parent.children.push(comment);

        const html = commentHtml(comment, getLevel(parentElement) + 1, parent);
        insertReplyComment(parentElement, html);
        updateChildIdsInParents(parentElement, [comment.public_id]);

        function insertReplyComment(parentElement, html) {
            const parentLevel = getLevel(parentElement);

            let next = parentElement.nextElementSibling;

            while (next) {
                const nextLevel = getLevel(next);

                if (nextLevel <= parentLevel) {
                    next.insertAdjacentHTML("beforebegin", html);
                    return;
                }

                next = next.nextElementSibling;
            }

            commentsContainer.insertAdjacentHTML("beforeend", html);
        }

        function getLevel(element) {
            return Number(
                [...element.classList]
                    .find(cls => cls.startsWith("level-"))
                    ?.replace("level-", "") || 0
            );
        }

        return true
    }

    function addNewComment(comment) {
        const text_comment = commentHtml(comment, 0, null);
        commentsContainer.insertAdjacentHTML("beforeend", text_comment);
        issue_comments.push(comment)
        return true
    }

    function findComment(comments, publicId) {
    for (const comment of comments) {
        if (comment.public_id === publicId) {return comment}
        const found = findComment(comment.children || [], publicId);
        if (found) {return found}
    }

    return null;
}
}

async function delete_comment(data) {
    const res = await api.del(window.data_url.comments(projectId,IssueId, data.id));
    if (!res || !res.ok) {return;}
    if (res.status === 204) {
        alert("Delete Complete!")
        delete_comment_in_ui(data.id)
    }
}

async function post_comment(event) {
    if (!text_area_comment.value.trim()) return;

    const url = window.data_url.comment(projectId,IssueId)
    const res = await api.post(url, {
        content: text_area_comment.value,
        parent_comment_public_id: text_area_comment.dataset.id || null,
    });
    if (!res || !res.ok) {return;}
    const comment = await res.json();

    text_area_comment.value = ""
    cancel_reply_comment()
    add_comment_in_ui(comment)
}

function updateChildIdsInParents(element, ids, action = "+") {
    let current = element;

    while (current) {
        const listIds = JSON.parse(current.dataset.listIds || "[]");

        if (action === "+") {
            for (const id of ids) {if (!listIds.includes(id)) {listIds.push(id)}}
        } else if (action === "-") {
            for (const id of ids) {
                const index = listIds.indexOf(id);
                if (index !== -1) {listIds.splice(index, 1)}
            }
        }

        if (listIds.length) {current.dataset.listIds = JSON.stringify(listIds)}
        else {delete current.dataset.listIds}

        const parentId = current.dataset.parent;
        if (!parentId) break;

        current = findCommentElement(parentId)
    }
}
// -----------------------------------------------------------------------------------------





// ----------------------------------------Issue Action-------------------------------------
function initIssueFieldEditors() {
    document.querySelectorAll(".info-item.editable").forEach(item => {
        item.addEventListener("click", () => {
            if (issue_full.status === "closed") {return;}
            openFieldEditor(item.dataset.field, item);
        });
    });

    function openFieldEditor(field, item) {
        switch (field) {
            case "status":
                editStatus(item);break;

            case "priority":
                editPriority(item);break;

            case "assignee":
                editAssignee();break;

            case "due_date":
                editDueDate(item);break;
        }
    }
}

async function OpenEditIssueWindow(event) {
    i_title.value = issue_full.title;
    i_description.value = issue_full.description;
    
    modal_issue.classList.remove("hidden");
}

async function applyEditTitle_and_Description(event) {
    event.preventDefault();

    const data_dict  = {title: i_title.value, description: i_description.value};
    const url = window.data_url.issue(projectId, IssueId);
    const response = await window.api.patch(url, data_dict);
    if (!response.ok) {return;}
    const issue = await response.json();
    
    change_UI_title_and_description(issue)
    close_issue_edit_window();
    alert("Update issue success!");
}

function close_issue_edit_window(event) {
    modal_issue.classList.add("hidden");
    form_issue.reset()
}

function reset_issue_form(event) {
    event.preventDefault();
    form_issue.reset()

}

function modal_issue_func(event) {
   if (event.target === modal_issue) {
       modal_issue.classList.add("hidden");
       form_issue.reset();
   }
}

function formatEnum(value) {
    return value
        .replaceAll("_", " ")
        .replace(/\b\w/g, c => c.toUpperCase());
}

async function issue_action(event) {
    event?.preventDefault();

    const element = event.target;

    const url_close = window.data_url.issueClose(projectId,IssueId);
    const url_reopen = window.data_url.issueReopen(projectId, IssueId);

    let res = false;

    const action = element.dataset.action;

    const result = confirm(`You want ${action.toUpperCase()} issue?`);

    if (!result) return;

    if (action !== "reopen") {res = await api.post(url_close)}
    else {res = await api.post(url_reopen)}


    if (!res || !res.ok) {return;}
    const issue = await res.json();

    change_UI_status_issue(issue)
}

function closeFieldModal() {
    fieldModal.classList.add("hidden");
    fieldModalBody.innerHTML = "";
}

function set_modal_data(text, options, value) {
    const field = `field-${text.toLowerCase()}`;
    fieldModalTitle.textContent = `Change ${text.toLowerCase()}`;
    fieldModalBody.innerHTML = `
        <label class="field-label" for="${field}">${text}</label>

        <select id="${field}" class="field-select">
            ${options.map(({ value, label }) => `
                <option value="${value}">${label}</option>
            `).join("")}
        </select>
    `;
    const select = document.querySelector(`#${field}`);
    select.value = value || "";
    return select
}

function create_map_list(list_values, isAssignee = false) {
    if (isAssignee) {
        return [
            { value: "", label: "Unassigned" },
            ...list_values.map(member => ({value: member.public_id, label: member.username}))
        ];
    }
    return list_values.map(value => ({value, label: formatEnum(value)}));
}

function editStatus() {
    const transitions = issue_statuses;

    fieldModalTitle.textContent = "Change status";
    const previous = transitions.previous
                        ? `<button type="button" class="status-option" data-status="${transitions.previous}">
                               ← ${formatEnum(transitions.previous)}
                           </button>`
                        : `<div class="status-empty">—</div>`
    const next = transitions.next
                        ? `<button type="button" class="status-option" data-status="${transitions.next}">
                               ${formatEnum(transitions.next)} →
                           </button>`
                        : `<div class="status-empty">—</div>`

    fieldModalBody.innerHTML = `
        <div class="status-modal">
            <div class="status-item">
                <span class="status-label">Previous</span>
                ${previous}
            </div>

            <div class="status-item current">
                <span class="status-label">Current</span>
                <div class="status-current status-option">${formatEnum(transitions.current)}</div>
            </div>

            <div class="status-item">
                <span class="status-label">Next</span>
                ${next}
            </div>
        </div>
    `;

    let selectedStatus = null;

    const options = fieldModalBody.querySelectorAll(".status-option");

    options.forEach(option => {
        option.addEventListener("click", () => {
            selectedStatus = option.dataset.status;

            // Снять выделение
            options.forEach(item => {
                item.classList.remove("status-current");
            });

            // Выделить выбранный
            option.classList.add("status-current");
        });
    });

    fieldModalSave.onclick = async () => {
        if (!selectedStatus) {return;}
        await updateStatus(selectedStatus);
    };

    fieldModal.classList.remove("hidden");

    async function updateStatus(status) {
        const url = window.data_url.issueEditStatus(projectId,IssueId);
        const data = {status: status};
        const res = await api.patch(url, data);
        if (!res || !res.ok) {return;}
        const issue = await res.json();
        change_UI_status_issue(issue)
        closeFieldModal();
    }
}

function editPriority() {
    const currentPriority = document.querySelector("#priority").textContent.trim().toLowerCase();
    const list_priorities = create_map_list(issue_priority);

    const select = set_modal_data("Priority", list_priorities, currentPriority)

    fieldModalSave.onclick = async () => {await updatePriority(select.value)};

    fieldModal.classList.remove("hidden");

    async function updatePriority(priority) {
        const url = window.data_url.issueEditPriority(projectId,IssueId);
        const data = {priority: priority};
        const res = await api.patch(url, data);

        if (!res || !res.ok) {return;}

        const issue = await res.json();
        change_UI_priority(issue)
        closeFieldModal();
    }
}

async function editAssignee() {
    const currentAssignee = document.querySelector("#assignee").dataset.publicId;
    const list_assignee = create_map_list(issue_assignee, true);

    const select = set_modal_data("Assignee", list_assignee, currentAssignee)

    fieldModalSave.onclick = async () => {await updateAssignee(select.value || null);};

    fieldModal.classList.remove("hidden");

    async function updateAssignee(assigneePublicId) {
        const url = window.data_url.issueEditAssignee(projectId, IssueId);
        const res = await api.patch(url, {assignee_id: assigneePublicId});

        if (!res || !res.ok) {return;}
        const issue = await res.json();
        change_UI_assignee(issue)
        closeFieldModal();
    }
}

function editDueDate() {
    const currentDueDate = document.querySelector("#due_time").dataset.value || "";

    fieldModalTitle.textContent = "Change due date";

    fieldModalBody.innerHTML = `
        <label class="field-label" for="field-due-date">Due date</label>
        <input id="field-due-date" class="field-input" type="datetime-local" value="${toDatetimeLocal(currentDueDate)}">
    `;

    const input = document.querySelector("#field-due-date");
    const get_dueDate = (input) =>  input.value ? new Date(input.value).toISOString() : null;

    fieldModalSave.onclick = async () => {await updateDueDate(get_dueDate(input));};

    fieldModal.classList.remove("hidden");

    async function updateDueDate(dueDate) {
        const url = window.data_url.issueEditDueDate(projectId,IssueId);
        const data = {due_date: dueDate};
        const res = await api.patch(url, data);

        if (!res || !res.ok) {return;}

        const issue = await res.json();
        change_UI_due_time(issue)
        closeFieldModal();
    }

    function toDatetimeLocal(value) {
        if (!value) {return "";}
        const date = new Date(value);
        const offset = date.getTimezoneOffset();
        const localDate = new Date(date.getTime() - offset * 60 * 1000);
        return localDate.toISOString().slice(0, 16);
    }
}

fieldModalClose.addEventListener("click", closeFieldModal);
fieldModalCancel.addEventListener("click", closeFieldModal);

fieldModal.addEventListener("click", (event) => {
    if (event.target === fieldModal) {
        closeFieldModal();
    }
});

// -----------------------------------------------------------------------------------------


loadIssue();
initIssueFieldEditors()