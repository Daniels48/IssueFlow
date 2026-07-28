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
        let cat_activity = this.notification.category === "activity";
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
                    ${cat_activity ? `<button class="notification-collapse">▼</button>` : ""}
                    <button class="notification-close">✕</button>
                </div>
            </div>
            <div class="notification-card-body">${this.renderBody()}</div>
        `;
        this.element = card;
        this.body = card.querySelector(".notification-card-body");
        this.bindEvents();
        if (this.collapsed) {this.collapse();}
        if (this.notification.category === "activity") {
        setTimeout(() => {if (!this.collapsed) {this.collapse();}}, 5000);}
        this.timeElement = card.querySelector(".notification-card-time");
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
        close.addEventListener("click", (e) => {
            e.stopPropagation();
            this.remove();
        });
        const collapse = this.element.querySelector(".notification-collapse");
        if (collapse) {
            collapse.addEventListener("click", (e) => {
                e.stopPropagation();
                this.toggle();
            });
        }
    }
    toggle() {
        if (this.collapsed) {this.expand();}
        else {this.collapse();}
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
    remove() {clearInterval(this.timer);notificationCenter.remove(this.notification.id);}
}

class BaseNotification {
    constructor(notification) {this.notification = notification;}
    row(label, value) {
        if (!value) {return "";}
        return `
            <div class="notification-row">
                <div class="notification-label">${label}</div>
                <div class="notification-value">${value}</div>
            </div>
        `;
    }

    message(text = this.notification.message) {
        if (!text) {
            return "";
        }

        return `
            <blockquote class="notification-message">
                ${text}
            </blockquote>
        `;
    }

    action() {
        if (!this.notification.action) {
            return "";
        }

        return `
            <a class="notification-open"
               href="${this.notification.action.url}">
                ${this.notification.action.text} →
            </a>
        `;
    }

    render() {
        return this.message() + this.action();
    }
}

class CommentNotification extends BaseNotification {
    render() {
        return `
            ${this.row("Project", this.notification.project.name)}
            ${this.row("Issue", this.notification.issue.title)}
            ${this.row("Author", this.notification.author.username)}
            ${this.message()}
            ${this.action()}
        `;
    }
}

class ProjectNotification extends BaseNotification {
    render() {
        return `
            ${this.row("Project", this.notification.project.name)}
            ${this.row("Owner", this.notification.author.username)}
            ${this.action()}
        `;
    }
}

class IssueNotification extends BaseNotification {
    render() {
        return `
            ${this.row("Project", this.notification.project.name)}
            ${this.row("Issue", this.notification.issue.title)}
            ${this.row("Author", this.notification.author.username)}
            ${this.action()}
        `;
    }
}

class UserRegisteredNotification extends BaseNotification {
    render() {
        return `
            <div class="notification-big-title">🎉 ${this.notification.author.username}</div>
            <div class="notification-description">Joined IssueFlow</div>
            ${this.action()}
        `;
    }

}

class UserNotification extends BaseNotification {
    render() {
        return ` ${this.message()}${this.action()}`;
    }
}

class ProjectMemberNotification extends BaseNotification {
    render() {
        return `
            ${this.row("Project", this.notification.project.name)}
            ${this.row("User", this.notification.member.username)}
            ${this.row("Role", this.notification.member.role)}
            ${this.action()}
        `;
    }
}

class NotificationFactory {
    static handlers = {
        "issue.comment.created": this.commentCreated,
        "issue.comment.updated": this.commentUpdated,
        "issue.comment.deleted": this.commentDeleted,

        "issue.created": this.issueCreated,
        "issue.updated": this.issueUpdated,
        "issue.deleted": this.issueDeleted,

        "issue.assigned": this.issueAssigned,
        "issue.unassigned": this.issueUnassigned,

        "issue.status.changed": this.issueStatusChanged,
        "issue.priority.changed": this.issuePriorityChanged,
        "issue.due_date.changed": this.issueDueDateChanged,

        "project.created": this.projectCreated,
        "project.updated": this.projectUpdated,
        "project.deleted": this.projectDeleted,

        "project.member.added": this.projectMemberAdded,
        "project.member.removed": this.projectMemberRemoved,
        "project.member.role.changed": this.projectMemberRoleChanged,

        "user.logged_in": this.userLoggedIn,
        "user.logged_out": this.userLoggedOut,
        "user.logged_out_all": this.userLoggedOutAll,
        "user.password.changed": this.userPasswordChanged,
        "user.email.verified": this.userEmailVerified,
        "user.deleted": this.userDeleted,
    };

    static fromEvent(event) {
        const handler = this.handlers[event.type];
        if (!handler) {
            console.warn(`Unknown notification type: ${event.type}`);
            return null;
        }
        return handler.call(this, event);
    }
    static create(event, data = {}) {
        return {
            id: crypto.randomUUID(),
            type: event.type,
            category: data.category ?? "activity",
            occurred_at: event.occurred_at ?? new Date().toISOString(),
            project: data.project ?? null,
            issue: data.issue ?? null,
            author: data.author ?? null,
            message: data.message ?? "",
            action: data.action ?? null,
        };
    }
    static getProject(event) {return event.project ?? null;}
    static getIssue(event) {return event.issue ?? null;}
    static getAuthor(event) {return event.author ?? null;}
    static openIssue(event) {
        if (!event.project?.public_id || !event.issue?.public_id) {return null;}
        return {
            text: "Open Issue",
            url: `/projects/${event.project.public_id}/issues/${event.issue.public_id}`,
        };
    }
    // -------------------------
    // COMMENTS
    // -------------------------
    static commentCreated(event) {
        return this.create(event, {
            category: "activity",
            project: this.getProject(event),
            issue: this.getIssue(event),
            author: this.getAuthor(event),
            message: event.comment.content,
            action: this.openIssue(event),
        });

    }
    static commentUpdated(event) {return this.commentCreated(event);}
    static commentDeleted(event) {return this.commentCreated(event);}
    // -------------------------
    // ISSUES
    // -------------------------
    static issueCreated(event) {
        return this.create(event, {
            category: "activity",
            project: this.getProject(event),
            issue: this.getIssue(event),
            author: this.getAuthor(event),
            message: event.title,
            action: this.openIssue(event),
        });
    }
    static issueUpdated(event) {return this.issueCreated(event);}
    static issueDeleted(event) {return this.issueCreated(event);}
    static issueAssigned(event) {
        return this.create(event, {
            category: "personal",
            project: this.getProject(event),
            issue: this.getIssue(event),
            author: this.getAuthor(event),
            message: `${event.author.username} assigned you to the issue.`,
            action: this.openIssue(event),
        });
    }
    static issueUnassigned(event) {return this.issueAssigned(event);}
    static issueStatusChanged(event) {return this.issueCreated(event);}
    static issuePriorityChanged(event) {return this.issueCreated(event);}
    static issueDueDateChanged(event) {return this.issueCreated(event);}
    // -------------------------
    // PROJECTS
    // -------------------------
    static projectCreated(event) {
        return this.create(event, {
            category: "activity",
            project: this.getProject(event),
            author: this.getAuthor(event),
            message: event.name,
        });
    }
    static projectUpdated(event) {return this.projectCreated(event);}
    static projectDeleted(event) {return this.projectCreated(event);}
    static projectMemberAdded(event) {return this.projectCreated(event);}
    static projectMemberRemoved(event) {return this.projectCreated(event);}
    static projectMemberRoleChanged(event) {return this.projectCreated(event);}
    // -------------------------
    // USER
    // -------------------------
    static userLoggedIn(event) {
        return this.create(event, {
            category: "personal",
            message: "Successful login.",
        });
    }
    static userLoggedOut(event) {return this.userLoggedIn(event);}
    static userLoggedOutAll(event) {return this.userLoggedIn(event);}
    static userPasswordChanged(event) {return this.userLoggedIn(event);}
    static userEmailVerified(event) {return this.userLoggedIn(event);}
    static userDeleted(event) {return this.userLoggedIn(event);}
}


window.notificationCenter = new NotificationCenter();
window.NotificationFactory = NotificationFactory
const NotificationRegistry = {

    "issue.created": {
        title: "Issue Created",
        icon: "📝",
        color: "#10b981",
        template: IssueNotification,
    },

    "issue.updated": {
        title: "Issue Updated",
        icon: "📝",
        color: "#3b82f6",
        template: IssueNotification,
    },

    "issue.deleted": {
        title: "Issue Deleted",
        icon: "🗑️",
        color: "#ef4444",
        template: IssueNotification,
    },

    "issue.assigned": {
        title: "Assigned",
        icon: "🎯",
        color: "#8b5cf6",
        template: IssueNotification,
    },

    "issue.unassigned": {
        title: "Unassigned",
        icon: "👤",
        color: "#64748b",
        template: IssueNotification,
    },

    "issue.status.changed": {
        title: "Status Changed",
        icon: "🔄",
        color: "#06b6d4",
        template: IssueNotification,
    },

    "issue.priority.changed": {
        title: "Priority Changed",
        icon: "⚡",
        color: "#f59e0b",
        template: IssueNotification,
    },

    "issue.due_date.changed": {
        title: "Due Date Changed",
        icon: "📅",
        color: "#f97316",
        template: IssueNotification,
    },

    "issue.comment.created": {
        title: "Comment Added",
        icon: "💬",
        color: "#3b82f6",
        template: CommentNotification,
    },

    "issue.comment.updated": {
        title: "Comment Updated",
        icon: "✏️",
        color: "#2563eb",
        template: CommentNotification,
    },

    "issue.comment.deleted": {
        title: "Comment Deleted",
        icon: "🗑️",
        color: "#dc2626",
        template: CommentNotification,
    },

    "project.created": {
        title: "Project Created",
        icon: "📁",
        color: "#10b981",
        template: ProjectNotification,
    },

    "project.updated": {
        title: "Project Updated",
        icon: "📁",
        color: "#3b82f6",
        template: ProjectNotification,
    },

    "project.deleted": {
        title: "Project Deleted",
        icon: "🗑️",
        color: "#ef4444",
        template: ProjectNotification,
    },

    "project.member.added": {
        title: "Member Added",
        icon: "👥",
        color: "#8b5cf6",
        template: ProjectMemberNotification,
    },

    "project.member.removed": {
        title: "Member Removed",
        icon: "👤",
        color: "#ef4444",
        template: ProjectMemberNotification,
    },

    "project.member.role.changed": {
        title: "Role Changed",
        icon: "🛡️",
        color: "#f59e0b",
        template: ProjectMemberNotification,
    },

    "user.registered": {
        title: "Welcome!",
        icon: "🎉",
        color: "#10b981",
        template: UserRegisteredNotification,
    },

    "user.email.verified": {
        title: "Email Verified",
        icon: "✅",
        color: "#10b981",
        template: UserNotification,
    },

    "user.password.changed": {
        title: "Password Changed",
        icon: "🔒",
        color: "#f59e0b",
        template: UserNotification,
    },

    "user.logged_in": {
        title: "Signed In",
        icon: "🔑",
        color: "#10b981",
        template: UserNotification,
    },

    "user.logged_out": {
        title: "Signed Out",
        icon: "🚪",
        color: "#64748b",
        template: UserNotification,
    },

    "user.logged_out_all": {
        title: "Signed Out Everywhere",
        icon: "🚪",
        color: "#ef4444",
        template: UserNotification,
    },

    "user.deleted": {
        title: "Account Deleted",
        icon: "🗑️",
        color: "#ef4444",
        template: UserNotification,
    },

};