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
const btn_close_issue = document.getElementById("close-issue");
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



btn_edit_issue.addEventListener("click", editIssue);
btn_close_issue.addEventListener("click", close_issue)
close_issue_modal.addEventListener("click", close_issue_func);
cancel_issue_form.addEventListener("click", reset_issue_form);
modal_issue.addEventListener("click", modal_issue_func);
i_apply.addEventListener("click", applyEdit);
commentsContainer.addEventListener("click", comments_action);
cancelReply.addEventListener("click", cancelReplyMode);


back_url.href = back_url.href + projectId;

btn_post_comment.addEventListener("click", post_comment);

async function comments_action(event) {
    const btn = event.target;

    const get_comment_container = value => value.parentElement.parentElement.parentElement;
    const get_value_comment = value => value.parentElement.previousElementSibling;
    const get_owner_comment = value => value.parentElement.previousElementSibling.previousElementSibling.firstElementChild;
    const get_id_comment = value => value.dataset.id;

    function get_data_comment(btn) {
        const container = get_comment_container(btn)
        const id_comment = get_id_comment(container)
        const obj_comment = get_value_comment(btn)
        const owner_comment = get_owner_comment(btn)

        return {
            id: id_comment,
            value: obj_comment.textContent,
            owner: owner_comment.textContent,
        }
    }


    if (btn.classList.contains("btn_reply")) {
        console.log("reply");
        const data = get_data_comment(btn)

        function startReply(data) {
            // replyingTo = comment.public_id;
            //
            // commentTitle.textContent = "Reply";

            replyAuthor.textContent = data.owner;
            replyPreview.textContent = data.value;
            text_area_comment.dataset.id = data.id;

            replyInfo.classList.remove("hidden");

            // postComment.textContent = "Post Reply";

            text_area_comment.focus();
        }

        startReply(data);
    }
    if (btn.classList.contains("btn_edit")) {
        console.log("edit");
        const data = get_data_comment(btn)
        console.log(data)
    }
    if (btn.classList.contains("btn_delete")) {
        console.log("del");
        const data = get_data_comment(btn)
        const res = await api.del(window.data_url.comments(projectId,IssueId, data.id));
        if (!res || !res.ok) {return;}
        if (res.status === 204) {
            const element = document.querySelector(`[data-id="${data.id}"]`);
            if (element) {element.remove();}
        }
    }
}

function cancelReplyMode() {
    // replyingTo = null;
    //
    // commentTitle.textContent = "Add Comment";

    replyInfo.classList.add("hidden");

    // postComment.textContent = "Post Comment";

    replyAuthor.textContent = "";
    replyPreview.textContent = "";
    text_area_comment.dataset.id = null;
}

async function loadIssue() {
    const res = await api.get(window.data_url.issue(projectId, IssueId));
    if (!res || !res.ok) {
        return;
    }
    const Issue = await res.json();
    renderIssueDetails(Issue, true);
    renderComments(Issue.comments);
}

function renderIssueDetails(issue, offload=false) {
    status.textContent = formatEnum(issue.status).toUpperCase();
    priority.textContent = issue.priority.toUpperCase();
    reporter.textContent = issue.reporter.username;
    assignee.textContent = issue.assignee?.username ?? "Unassigned";
    due_time.textContent = formatDate(issue.due_date);
    created_time.textContent = formatDate(issue.created_at);
    updated_time.textContent = formatRelativeDate(issue.updated_at);
    title.textContent = issue.title;
    head_status.textContent = formatEnum(issue.status).toUpperCase();
    head_priority.textContent = issue.priority.toUpperCase();
    description.textContent = issue.description;

    if (offload !== false) {
        const count = countComments(issue.comments);
        len_comments.textContent = `${count} comment${count === 1 ? "" : "s"}`;
    }
    function formatDate(dateString) {
    if (!dateString) return "—";

    return new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
    }).format(new Date(dateString));
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

    function countComments(comments) {
        return comments.reduce((count, comment) => {
            return count + 1 + countComments(comment.children);
        }, 0);
    }
}

function renderComments(comments) {
    if (comments.length === 0) {
        commentsContainer.innerHTML = commentsContainer.innerHTML + `<div class="empty">No comments</div>`;
        return;
    }

    commentsContainer.innerHTML = commentsContainer.innerHTML + renderTree(comments);

    function renderTree(comments, level = 0, parent = null) {
    let html = ``;
    for (const comment of comments) {
        html += commentHtml(comment, level, parent);
        if (comment.children.length) {html += renderTree(comment.children, level + 1, comment)}
    }
    return html;
}

    function commentHtml(comment, level, parent) {
        const visualLevel = Math.min(level, 3);

        return `
            <article data-id="${comment.public_id}" class="comment level-${visualLevel} card">
                <div class="avatar">${getInitial(comment.author.username)}</div>
                <div class="comment-content">
                   ${parent ? commentReply(parent) : ""}
                    <div class="comment-header">
                        <strong>${comment.author.username}</strong>
                        <span>${formatDateTime(comment.created_at)}</span>
                    </div>
                    <p>${comment.content}</p>
                    <div class="comment-actions">
                        <button class="btn_reply">Reply</button>
                        <button class="btn_edit">Edit</button>
                        <button class="btn_delete">Delete</button>
                    </div>
                </div>
            </article>
            <button class="toggle-replies">
                ▼ 4 replies
            </button>
        `;
    }

    function commentReply(parent) {
        return `
            <div class="reply-preview">
                <span>Replying to ${parent.author.username}</span>
                <blockquote>${parent.content}</blockquote>
            </div>
        `;
    }

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

    function getInitial(text) {
        if (!text) return "";
        return text.charAt(0).toUpperCase();
    }
}

async function post_comment(event) {
    const id_reply = text_area_comment.dataset.id;
    const data = {content: text_area_comment.value, parent_comment_public_id: id_reply}
    const res = await api.post(window.data_url.comment(projectId,IssueId), data);
    if (!res || !res.ok) {return;}
    const comment = await res.json();
}

function formatEnum(value) {
    return value
        .replaceAll("_", " ")
        .replace(/\b\w/g, c => c.toUpperCase());
}

function unformatEnum(value) {
    return value
        .toLowerCase()
        .replaceAll(" ", "_");
}

async function editIssue(event) {
    const response = await window.api.get(window.data_url.issueEdit(projectId, IssueId));
    if (!response.ok) {return;}
    const issue = await response.json();

    i_title.value = issue.title;
    i_description.value = issue.description;
    i_priority.value = issue.priority;
    i_due_date.value = issue.due_date.slice(0, 10);
    i_assignee.innerHTML = set_assignee_html(issue);
    i_status.innerHTML = set_status_html(issue);

    function set_assignee_html(issue) {
        let html = `<option value="" disabled ${!issue.assignee ? "selected" : ""}>Choose member</option>`;
        for (const member of issue.members) {
        html += member_text(member);
    }
        function member_text(member) {
            const selected = member.public_id === issue.assignee?.public_id ? "selected" : "";

            return `<option value="${member.public_id}" ${selected}>${member.username}</option>`;
        }
        return html
    }

    function set_status_html(issue) {
        let html = ``;
        for (const status of issue.statuses) {html += status_text(status);}
        function status_text(status) {
            const selected = issue.status === status ? "selected" : "";

            return `<option ${selected}>${formatEnum(status)}</option>`;
        }
        return html
    }

    modal_issue.classList.remove("hidden");
}

async function applyEdit(event) {
    event.preventDefault();
    const option = i_assignee.selectedOptions[0];
    const publicId = option?.value ?? null;

    const data_dict  = {
            title: i_title.value,
            description: i_description.value,
            assignee_public_id: publicId || null,
            status:unformatEnum(i_status.value),
            priority:i_priority.value,
            due_date:i_due_date.value,
    }
    const response = await window.api.patch(window.data_url.issue(projectId, IssueId), data_dict);
    if (!response.ok) {return;}
    const issue = await response.json();
    renderIssueDetails(issue);
    close_issue_func();
    alert("Update issue success!");
}

async function close_issue(event) {

}

function close_issue_func(event) {
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



loadIssue();