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



// ---------------------------------------Head----------------------------------------------
function change_UI_status_issue(issue) {
    head_status.textContent = formatEnum(issue.status).toUpperCase();
    status.textContent = formatEnum(issue.status).toUpperCase();
    if (issue.status === "closed") {
        btn_issue_action.dataset.action = "reopen";
        btn_issue_action.textContent = "Reopen";
    } else {
        btn_issue_action.dataset.action = "close";
        btn_issue_action.textContent = "Close";
    }
}

function change_UI_title_and_description(issue) {
    title.textContent = issue.title;
    description.textContent = issue.description;
}

function change_UI_due_time(issue) {
    due_time.textContent = issue.due_date ? formatDate(issue.due_date) : "No due date";
    due_time.dataset.value = issue.due_date ? issue.due_date.slice(0, 16) : "";
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
    updated_time.textContent = formatRelativeDate(issue.updated_at);
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
}

function renderIssueDetails(issue, offload=false) {
    reporter.textContent = issue.reporter.username;
    created_time.textContent = formatDate(issue.created_at);

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

function renderComments(comments) {
    if (comments.length === 0) {
        const empty_text = `<div class="empty">No comments</div>`;
        commentsContainer.insertAdjacentHTML("beforeend", empty_text);
        return;
    }

    commentsContainer.insertAdjacentHTML("beforeend", renderTree(comments));

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
    const visualLevel = Math.min(level, 3);

    function formatDateTime(dateString) {
        if (!dateString) return "—";
        const date = new Date(dateString);
        const datePart = new Intl.DateTimeFormat("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric",
        }).format(date);
        const timePart = new Intl.DateTimeFormat("en-US", {
            hour: "2-digit",
            minute: "2-digit",
            hour12: false,
        }).format(date);
        return `${datePart} • ${timePart}`;
    }

    function childrenAttribute(comment) {
        if (!comment.children?.length) {return "";}
        return `data-list-ids='${JSON.stringify(getChildrenIds(comment))}'`;
    }

    function getChildrenIds(comment) {
        const ids = [];

        function walk(node) {
            for (const child of node.children) {
                ids.push(child.public_id);
                walk(child);
            }
        }

        walk(comment);

        return ids;
    }

    function getInitial(text) {
        if (!text) return "";
        return text.charAt(0).toUpperCase();
    }

    function commentReply(parent) {
    return `
        <div class="reply-preview">
            <span>Replying to ${parent.author.username}</span>
            <blockquote>${parent.content}</blockquote>
        </div>
    `;
}

    function isEdited(comment) {
        return (
            comment.updated_at &&
            Math.abs(new Date(comment.updated_at) - new Date(comment.created_at)) > 1000
        );
    }

    const update_time = comment => isEdited(comment) ? `edited ${formatRelativeDate(comment.updated_at)}` : "";

    const set_parent_id = parent => parent ? `data-parent="${parent.public_id}"` : "";

    let z = `<button class="toggle-replies">▼ 4 replies</button>`

    return `
        <article ${set_parent_id(parent)} ${childrenAttribute(comment)} data-id="${comment.public_id}" class="comment level-${visualLevel} card">
            <div class="avatar">${getInitial(comment.author.username)}</div>
            <div class="comment-content">
                <div class="comment-header">
                    <strong class="comment-owner" data-owner="${comment.author.username}">${comment.author.username}</strong>
                    <span class="comment-create-date">${formatDateTime(comment.created_at)}</span>
                </div>
                
                ${parent ? commentReply(parent) : ""}
                
                <div class="comment-head">
                    <p class="content-comment" data-text="${comment.content}">${comment.content}</p>
                    <div class="comment-meta">${update_time(comment)}</div>
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
        </article>
    `;
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
    const head_container = data.container.querySelector(".comment-head");
    const edit_container = data.container.querySelector(".comment-edit");

    return {
        head_container: head_container,
        edit_container: edit_container
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


    function autoResize(textarea) {
        textarea.style.height = "0";
        textarea.style.height = textarea.scrollHeight + "px";
    }

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
        edit_string.textContent = "edited " + formatRelativeDate(comment.updated_at)
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

async function delete_comment(data) {
        const res = await api.del(window.data_url.comments(projectId,IssueId, data.id));
        if (!res || !res.ok) {return;}
        if (res.status === 204) {
            alert("Delete Complete!")
            const element = document.querySelector(`[data-id="${data.id}"]`);
            if (element) {
                if (element?.dataset.listIds) {
                    const ids = JSON.parse(element.dataset.listIds);
                    for (const id of ids) {
                        const comment = document.querySelector(`[data-id="${id}"]`);
                        if (comment) {comment.remove()}
                    }
                }
                element.remove();
                const count = commentsContainer.children.length - 1;
                set_count_comments(count);
            }
        }
}

async function post_comment(event) {
    if (text_area_comment.value.length > 1) {
        const data = {
            content: text_area_comment.value,
            parent_comment_public_id: text_area_comment.dataset.id || null,
        };
        const res = await api.post(window.data_url.comment(projectId,IssueId), data);
        if (!res || !res.ok) {return;}
        const comment = await res.json();
        text_area_comment.value = ""
        cancel_reply_comment()
        if (data.parent_comment_public_id) {

        } else {
            const text_comment = commentHtml(comment, 0, null);
            commentsContainer.insertAdjacentHTML("beforeend", text_comment);
        }
        const count = parseInt(len_comments.textContent, 10);
        set_count_comments(count + 1);
    }
}
// -----------------------------------------------------------------------------------------





// ----------------------------------------Issue Action-------------------------------------
async function OpenEditIssueWindow(event) {
    const response = await window.api.get(window.data_url.issueEdit(projectId, IssueId));
    if (!response.ok) {return;}
    const issue = await response.json();

    i_title.value = issue.title;
    i_description.value = issue.description;
    
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

async function issue_action(event) {
    event?.preventDefault();

    const url = window.data_url.issueClose(projectId,IssueId);
    const res = await api.post(url);
    if (!res || !res.ok) {return;}

    const issue = await res.json();

    // closeFieldModal();
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
    const currentStatus = document.querySelector("#status").textContent.trim().toLowerCase();
    console.log(currentStatus)
    const list_statuses = create_map_list(issue_full.statuses);

    const select = set_modal_data("Status", list_statuses, currentStatus)

    fieldModalSave.onclick = async () => {await updateStatus(select.value)};

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
    const list_priorities = create_map_list(issue_full.priorities);

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
    const list_assignee = create_map_list(issue_full.members, true);

    const select = set_modal_data("Assignee", list_assignee, currentAssignee)

    fieldModalSave.onclick = async () => {await updateAssignee(select.value || null);};

    fieldModal.classList.remove("hidden");

    async function updateAssignee(assigneePublicId) {
        const url = window.data_url.issueEditAssignee(projectId, IssueId);
        const res = await api.patch(url, {assignee_public_id: assigneePublicId});

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

// -----------------------------------------------------------------------------------------



function formatEnum(value) {
    return value
        .replaceAll("_", " ")
        .replace(/\b\w/g, c => c.toUpperCase());
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


function initIssueFieldEditors() {
    document.querySelectorAll(".info-item.editable").forEach(item => {
        item.addEventListener("click", () => {
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

function formatDate(dateString) {
    if (!dateString) return "—";

    const date = new Date(dateString);

    const datePart = new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
    }).format(date);

    const timePart = new Intl.DateTimeFormat("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
    }).format(date);

    return `${datePart}  •  ${timePart}`;
}

function closeFieldEditor() {
    document.querySelectorAll(".field-dropdown").forEach(dropdown => {
        dropdown.remove();
    });
}



function closeFieldModal() {
    fieldModal.classList.add("hidden");
    fieldModalBody.innerHTML = "";
}

fieldModalClose.addEventListener("click", closeFieldModal);
fieldModalCancel.addEventListener("click", closeFieldModal);

fieldModal.addEventListener("click", (event) => {
    if (event.target === fieldModal) {
        closeFieldModal();
    }
});

loadIssue();
initIssueFieldEditors()