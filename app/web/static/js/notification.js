"use strict";


class NotificationCenter {
    constructor() {
        this.personal = [];
        this.activity = [];

        this.isOpen = false;
        this.showAllActivity = false;
        this.personalCollapsed = false;
        this.activityCollapsed = false;

        this.button = document.getElementById("notification-button");
        this.center = document.getElementById("notification-center");

        this.personalContainer = document.getElementById("notification-personal");
        this.activityContainer = document.getElementById("notification-activity");

        this.personalCount = document.getElementById("personal-count");
        this.activityCount = document.getElementById("activity-count");
        this.counter = document.getElementById("notification-counter");

        this.clearButton = document.getElementById("notification-clear");
        this.showMoreButton = document.getElementById("notification-show-more");

        this.personalToggle = document.getElementById("personal-toggle");
        this.personalClear = document.getElementById("personal-clear");

        this.activityToggle = document.getElementById("activity-toggle");
        this.activityClear = document.getElementById("activity-clear");
        this.bindEvents();
    }
    bindEvents() {
        this.button.addEventListener("click", () => this.toggle());
        this.clearButton.addEventListener("click", () => this.clear());
        this.showMoreButton.addEventListener("click", () => {
            this.showAllActivity = !this.showAllActivity;
            this.render();
        });
        this.personalToggle.addEventListener("click", () => {
            this.personalCollapsed = !this.personalCollapsed;
            this.render();
        });

        this.activityToggle.addEventListener("click", () => {
            this.activityCollapsed = !this.activityCollapsed;
            this.render();
        });

        this.personalClear.addEventListener("click", () => {
            this.clearPersonal();
        });

        this.activityClear.addEventListener("click", () => {
            this.clearActivity();
        });
    }
    toggle() {
        this.isOpen = !this.isOpen;
        this.center.classList.toggle("hidden", !this.isOpen);
    }
    add(notification) {
        if (notification.category === "personal") {this.personal.unshift(notification);}
        else {this.activity.unshift(notification);}
        this.render();
    }
    remove(id) {
        this.personal = this.personal.filter(n => n.id !== id);
        this.activity = this.activity.filter(n => n.id !== id);
        this.render();
    }
    clear() {
        this.personal = [];
        this.activity = [];
        this.render();
    }
    updateCounter() {
        const total = this.personal.length + this.activity.length
        this.counter.textContent = total > 99 ? "99+" : total;
        this.counter.classList.toggle("hidden", total === 0);
        this.personalCount.textContent = `(${this.personal.length})`;
        this.activityCount.textContent = `(${this.activity.length})`;
    }
    renderList(container, notifications) {
        container.innerHTML = "";

        for (const notification of notifications) {
            const card = new NotificationCard(notification);
            container.appendChild(card.render());
        }
    }
    render() {
        this.updateCounter();
        this.personalContainer.innerHTML = "";
        this.activityContainer.innerHTML = "";
        this.renderList(this.personalContainer, this.personal);
        const activity = this.showAllActivity ? this.activity : this.activity.slice(0, 5);
        this.renderList(this.activityContainer, activity);
        const hidden = this.activity.length - activity.length;
        if (hidden > 0) {
            this.showMoreButton.classList.remove("hidden");
            this.showMoreButton.textContent = this.showAllActivity
                ? "Hide older notifications" : `Show ${hidden} older notifications`;
        } else {this.showMoreButton.classList.add("hidden");}
        if (this.activityCollapsed) {
            this.activityContainer.classList.add("hidden");
            this.activityToggle.textContent = "▶";
        } else {
            this.activityContainer.classList.remove("hidden");
            this.activityToggle.textContent = "▼";
        }
        if (this.personalCollapsed) {
            this.personalContainer.classList.add("hidden");
            this.personalToggle.textContent = "▶";
        } else {
            this.personalContainer.classList.remove("hidden");
            this.personalToggle.textContent = "▼";
        }
    }
    clearActivity() {
        this.activity = [];
        this.render();
    }
    clearPersonal() {
        this.personal = [];
        this.render();
    }
}

class NotificationCard {
    constructor(notification) {
        this.notification = notification;

        this.collapsed = notification.collapsed ?? false;

        this.element = null;
        this.body = null;
        this.timeElement = null;

        this.timer = null;
        this.collapseTimer = null;
    }

    getType() {
        return NotificationRegistry[this.notification.type] ?? {
            title: "Notification",
            icon: "🔔",
            color: "#64748b",
            template: BaseNotification,
        };
    }

    getTime() {
        const occurred = new Date(this.notification.occurred_at);
        const now = new Date();
        const seconds = Math.floor((now - occurred) / 1000);
        if (seconds < 60) {return "just now";}
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) {return `${minutes} min ago`;}
        const hours = Math.floor(minutes / 60);
        if (hours < 24) {return `${hours} h ago`;}
        const days = Math.floor(hours / 24);
        if (days < 7) {return `${days} d ago`;}
        return occurred.toLocaleDateString();
    }

    render() {
        const card = document.createElement("article");
        card.className = "notification-card";
        const isActivity = this.notification.category === "activity";
        const type = this.getType();
        card.style.borderLeftColor = type.color;
        card.innerHTML = `
            <div class="notification-card-header">
                <div class="notification-card-title">
                    <span class="notification-icon">${type.icon}</span>
                    <span>${type.title}</span>
                </div>

                <div class="notification-card-actions">
                    <span class="notification-card-time"></span>
                    ${isActivity ? `<button class="notification-collapse">▼</button>` : ""}
                    <button class="notification-close">✕</button>
                </div>
            </div>
            <div class="notification-card-body">${this.renderBody()}</div>
        `;

        this.element = card;
        this.body = card.querySelector(".notification-card-body");
        this.timeElement = card.querySelector(".notification-card-time");
        this.bindEvents();
        if (this.collapsed) {this.collapse();}
        if (isActivity) {
            this.collapseTimer = setTimeout(() => {if (!this.collapsed) {this.collapse();}}, 5000);
        }
        this.timeElement.textContent = this.getTime();
        this.timer = setInterval(() => {this.timeElement.textContent = this.getTime();}, 60000);
        return card;
    }

    renderBody() {
        const type = this.getType();
        return new type.template(this.notification).render();
    }

    bindEvents() {
        const close = this.element.querySelector(".notification-close");

        close.addEventListener("click", (event) => {
            event.stopPropagation();
            this.remove();
        });

        const collapse = this.element.querySelector(".notification-collapse");

        if (collapse) {
            collapse.addEventListener("click", (event) => {
                event.stopPropagation();
                this.toggle();
            });
        }
    }

    toggle() {
        if (this.collapsed) {this.expand();
        } else {this.collapse();}
    }

    collapse() {
        this.collapsed = true;
        this.body.style.display = "none";
        const button = this.element.querySelector(".notification-collapse");
        if (button) {button.textContent = "▶";}
    }

    expand() {
        this.collapsed = false;
        this.body.style.display = "";
        const button = this.element.querySelector(".notification-collapse");
        if (button) {button.textContent = "▼";}
    }

    remove() {
        clearInterval(this.timer);
        clearTimeout(this.collapseTimer);
        notificationCenter.remove(this.notification.id);
    }
}

class BaseNotification {
    constructor(notification) {this.notification = notification;}

    row(label, value) {
        if (!value) {return "";}

        return `<div class="notification-row">
                    <div class="notification-label">${label}</div>
                    <div class="notification-value">${value}</div>
                </div>`;
    }

    message(text = this.notification.message) {
        if (!text) {return "";}
        return `<blockquote class="notification-message">${text}</blockquote>`;
    }

    action() {
        const action = this.notification.action;
        if (!action) {return "";}
        return `<a class="notification-open" href="${action.url}">${action.text} →</a>`;
    }

    render() {return `${this.message()}${this.action()}`;}
}

class NotificationFactory {
    static handlers = {
        "project.created": this.projectCreated,
        "project.updated": this.projectUpdated,
        "project.deleted": this.projectDeleted,

        "project.member.added": this.projectMemberAdded,
        "project.member.removed": this.projectMemberRemoved,
        "project.member.role.changed": this.projectMemberRoleChanged,

        "issue.created": this.issueCreated,
        "issue.updated": this.issueUpdated,
        "issue.deleted": this.issueDeleted,

        "issue.assigned": this.issueAssigned,
        "issue.unassigned": this.issueUnassigned,

        "issue.status.changed": this.issueStatusChanged,
        "issue.priority.changed": this.issuePriorityChanged,
        "issue.due_date.changed": this.issueDueDateChanged,

        "issue.closed": this.issueClosed,
        "issue.reopened": this.issueReopened,

        "issue.comment.created": this.commentCreated,
        "issue.comment.updated": this.commentUpdated,
        "issue.comment.deleted": this.commentDeleted,

        "user.logged_in": this.userLoggedIn,
        "user.logged_out": this.userLoggedOut,
        "user.logged_out_all": this.userLoggedOutAll,
        "user.password.changed": this.userPasswordChanged,
        "user.email.verified": this.userEmailVerified,
        "user.deleted": this.userDeleted,
    };

    static fromEvent(event) {
        const handler = this.handlers[event.event_type];

        if (!handler) {
            console.warn(`Unknown notification type: ${event.event_type}`);
            return null;
        }

        const data = {
            event_type: event.event_type,
            ...event.payload,
        };

        return handler.call(this, data);
    }

    static getType(event) {
        const eventType = event.event_type;

        if (eventType.startsWith("project.member.")) {return "member";}

        if (eventType.startsWith("issue.comment.")) {return "comment";}

        if (eventType.startsWith("project.")) {return "project";}

        if (eventType.startsWith("issue.")) {return "issue";}

        if (eventType.startsWith("user.")) {return "user";}

        return "unknown";
    }

    static create(event, {category = "activity", message = "", action = null} = {}) {
        return {
            id: crypto.randomUUID(),
            type: this.getType(event),
            category,
            message,
            action,
            occurred_at: event.occurred_at,
        };
    }

    static openIssue(event) {
        if (!event.project?.public_id || !event.issue?.public_id) {
            return null;
        }

        return {
            text: "Open Issue",
            url: `/projects/${event.project.public_id}/issues/${event.issue.public_id}`,
        };
    }

    static openProject(event) {
        if (!event.project?.public_id) {return null;}

        return {
            text: "Open Project",
            url: `/projects/${event.project.public_id}`,
        };
    }

    static is_personal(obj) {
        return obj?.public_id === window.user?.public_id;
    }

    static truncate(text, maxLength = 30) {
        if (typeof text !== "string") {return "";}

        return text.length > maxLength
            ? `${text.slice(0, maxLength - 3)}...`
            : text;
    }

    static formatStatus(status) {
        const statuses = {
            open: "Open",
            in_progress: "In progress",
            closed: "Closed",
        };

        return statuses[status] ?? status;
    }

    static formatPriority(priority) {
        const priorities = {
            low: "Low",
            medium: "Medium",
            high: "High",
            critical: "Critical",
        };

        return priorities[priority] ?? priority;
    }

    static formatDueDate(date) {
        if (!date) {return null;}
        const parsed = new Date(date);
        if (Number.isNaN(parsed.getTime())) {return null;}

        const parts = new Intl.DateTimeFormat("en-GB", {
            day: "2-digit",
            month: "2-digit",
            year: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            hour12: false,
        }).formatToParts(parsed);

        const values = Object.fromEntries(parts.map(part => [part.type, part.value]));

        return `${values.day}.${values.month}.${values.year} ` + `${values.hour}:${values.minute}`;
    }

    static value(value) {
        return `<span class="notification-value">${value}</span>`;
    }

    static strongValue(value) {
        return `<strong class="notification-value">${value}</strong>`;
    }

    // PROJECTS

    static projectCreated(event) {
        const data = this.get_memberData(event)
        return this.create(event, {
            category: "activity",
            message: `${data.author} created project "${data.project}".`,
            action: this.openProject(event),
        });
    }

    static projectUpdated(event) {
        const data = this.get_memberData(event)
        return this.create(event, {
            category: "activity",
            message: `${data.author} updated project "${data.project}".`,
            action: this.openProject(event),
        });
    }

    static projectDeleted(event) {
        const data = this.get_memberData(event)
        return this.create(event, {
            category: "activity",
            message: `${data.author} deleted project "${data.project}".`,
        });
    }

    // MEMBERS

    static get_memberData(event){
        return {
            project: this.value(this.truncate(event.project?.name ?? "Untitled project")),
            username: this.strongValue(event.user?.username ?? "member"),
            author: this.strongValue(event.author?.username ?? "Someone"),
            oldRole: this.strongValue(event.old_value ?? null),
            newRole: this.strongValue(event.member?.role ?? null),
        }
    }

    static projectMemberAdded(event) {
        const data = this.get_memberData(event)

        return this.create(event, {
            category: "activity",
            message: `${data.author} added ${data.username} to "${data.project}".`,
            action: this.openProject(event),
        });
    }

    static projectMemberRemoved(event) {
        const data = this.get_memberData(event)

        return this.create(event, {
            category: "activity",
            message: `${data.author} removed ${data.username} from "${data.project}".`,
            action: this.openProject(event),
        });
    }

    static projectMemberRoleChanged(event) {
        const data = this.get_memberData(event)

        return this.create(event, {
            category: "activity",
            message:
                `${data.author} changed ${data.username}'s role in "${data.project}" ` +
                `from ${data.oldRole} to ${data.newRole}.`,
            action: this.openProject(event),
        });
    }

    // ISSUES

    static get_issueData(event) {
        return {
            author: this.strongValue(event.author?.username ?? "Someone"),
            title: this.strongValue(this.truncate(event.issue?.title ?? "Untitled issue")),
            old_user: this.strongValue(event.old_value?.username ?? null),
            new_user: this.strongValue(event.new_value?.username ?? null),
            old_status: this.strongValue(event.old_value ? this.formatStatus(event.old_value) : null),
            new_status: this.strongValue(event.new_value ? this.formatStatus(event.new_value) : null),
            old_priority: this.strongValue(event.old_value ? this.formatPriority(event.old_value) : null),
            new_priority: this.strongValue(event.new_value ? this.formatPriority(event.new_value) : null),
            old_date: this.strongValue(event.old_value ? this.formatDueDate(event.old_value) : null),
            new_date: this.strongValue(event.new_value ? this.formatDueDate(event.new_value) : null),
        };
    }

    static issueCreated(event) {
        const data = this.get_issueData(event)
        return this.create(event, {
            category: "activity",
            message: `${data.author} created issue "${data.title}".`,
            action: this.openIssue(event),
        });
    }

    static issueUpdated(event) {
        const data = this.get_issueData(event)
        return this.create(event, {
            category: "activity",
            message: `${data.author} updated issue "${data.title}".`,
            action: this.openIssue(event),
        });
    }

    static issueDeleted(event) {
        const data = this.get_issueData(event)
        return this.create(event, {
            category: "activity",
            message: `${data.author} deleted issue "${data.title}".`,
        });
    }

    static issueAssigned(event) {
        const personal = this.is_personal(event.new_value);
        const data = this.get_issueData(event);

        let message;

        if (personal) {
            message = `${data.author} assigned you to "${data.title}".`;
        } else if (data.old_user) {
            message = `${data.author} reassigned "${data.title}" from ${data.old_user} to ${data.new_user}.`;
        } else {
            message = `${data.author} assigned ${data.new_user} to "${data.title}".`;
        }

        return this.create(event, {
            category: personal ? "personal" : "activity",
            message,
            action: this.openIssue(event),
        });
    }

    static issueUnassigned(event) {
        const personal = this.is_personal(event.old_value);
        const data = this.get_issueData(event);
        const pre_msg = personal ? "you": `${data.old_user}`;
        const message = `${data.author} unassigned ${pre_msg} from "${data.title}".`

        return this.create(event, {
            category: personal ? "personal" : "activity",
            message,
            action: this.openIssue(event),
        });
    }

    static issueStatusChanged(event) {
        const data = this.get_issueData(event);

        return this.create(event, {
            category: "activity",
            message: `${data.author} changed the status of "${data.title}" from ${data.old_status} to ${data.new_status}.`,
            action: this.openIssue(event),
        });
    }

    static issuePriorityChanged(event) {
        const data = this.get_issueData(event);

        return this.create(event, {
            category: "activity",
            message: `${data.author} changed the priority of "${data.title}" from ${data.old_priority} to ${data.new_priority}.`,
            action: this.openIssue(event),
        });
    }

    static issueDueDateChanged(event) {
        const data = this.get_issueData(event);

        return this.create(event, {
            category: "activity",
            message: `${data.author} changed the due date of "${data.title}" from ${data.old_date} to ${data.new_date}.`,
            action: this.openIssue(event),
        });
    }

    static issueClosed(event) {
        const data = this.get_issueData(event);

        return this.create(event, {
            category: "activity",
            message: `${data.author} closed "${data.title}".`,
            action: this.openIssue(event),
        });
    }

    static issueReopened(event) {
        const data = this.get_issueData(event);

        return this.create(event, {
            category: "activity",
            message: `${data.author} reopened "${data.title}".`,
            action: this.openIssue(event),
        });
    }

    // COMMENTS

    static get_dataComment(event) {
        const title = this.value(this.truncate(event.issue?.title ?? "Untitled issue"));
        const content = this.value(this.truncate(event.comment?.content ?? ""));
        const author = this.strongValue(event.author?.username ?? "Someone");
        const parentAuthor = this.strongValue(event.parent?.author?.username ?? "someone");

        return {
            title: title,
            content: content,
            author: author,
            parentAuthor: parentAuthor,
        }
    }

    static commentCreated(event) {
        const data = this.get_dataComment(event);
        const personal = event.parent?.author?.public_id === window.user?.public_id;

        let middleText;

        if (event.parent) {middleText = personal ? "replied to your comment" : `replied to ${data.parentAuthor}`}
        else {middleText = "commented";}

        const message = `${data.author} ${middleText} on "${data.title}": "${data.content}"`;

        return this.create(event, {
            category: personal ? "personal" : "activity",
            message,
            action: this.openIssue(event),
        });
    }

    static commentUpdated(event) {
        const data = this.get_dataComment(event)

        return this.create(event, {
            category: "activity",
            message: `${data.author} edited a comment on "${data.title}".`,
            action: this.openIssue(event),
        });
    }

    static commentDeleted(event) {
        const data = this.get_dataComment(event)

        return this.create(event, {
            category: "activity",
            message: `${data.author} deleted a comment from "${data.title}".`,
            action: this.openIssue(event),
        });
    }


    // USER

    static userLoggedIn(event) {
        return this.create(event, {
            category: "personal",
            message: "Successful login.",
        });
    }

    static userLoggedOut(event) {
        return this.userLoggedIn(event);
    }

    static userLoggedOutAll(event) {
        return this.userLoggedIn(event);
    }

    static userPasswordChanged(event) {
        return this.userLoggedIn(event);
    }

    static userEmailVerified(event) {
        return this.userLoggedIn(event);
    }

    static userDeleted(event) {
        return this.userLoggedIn(event);
    }
}


window.notificationCenter = new NotificationCenter();
window.NotificationFactory = NotificationFactory
const NotificationRegistry = {
    project: {
        title: "Project",
        icon: "📁",
        color: "#...",
        template: BaseNotification,
    },

    issue: {
        title: "Issue",
        icon: "📋",
        color: "#...",
        template: BaseNotification,
    },

    member: {
        title: "Member",
        icon: "👤",
        color: "#...",
        template: BaseNotification,
    },

    comment: {
        title: "Comment",
        icon: "💬",
        color: "#...",
        template: BaseNotification,
    },

    user: {
        title: "User",
        icon: "👤",
        color: "#...",
        template: BaseNotification,
    },
};