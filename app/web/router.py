from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from fastapi.responses import RedirectResponse
from app.modules.auth.dependencies import CurrentUser

router = APIRouter()


templates = Jinja2Templates(directory="app/web/templates")


@router.get("/")
async def index(request: Request):
    list_js_files = ["index"]
    list_css_files = ["index", "base"]
    return templates.TemplateResponse(request=request, name="index.html",
        context={
            "title": "IssueFlow",
            "css_files": list_css_files,
            "js_files": list_js_files,
        })


@router.get("/projects")
async def projects(request: Request):
    list_js_files = ["projects"]
    list_css_files = ["projects", "base"]
    return templates.TemplateResponse(request=request, name="projects.html",
        context={
            "title": "Projects • IssueFlow",
            "css_files": list_css_files,
            "js_files": list_js_files,
        })


@router.get("/projects/{project_id}")
async def project(request: Request, project_id: UUID):
    list_js_files = ["project"]
    list_css_files = ["modal_member", "project", "base"]
    return templates.TemplateResponse(request=request,name="project.html",
        context={
            "title": "Project • IssueFlow",
            "css_files": list_css_files,
            "js_files": list_js_files,
        },
    )


@router.get("/projects/{project_id}/issues/{issue_id}")
async def issue(request: Request, project_id: UUID, issue_id: UUID):
    list_js_files = ["issue"]
    list_css_files = ["issue", "base"]
    return templates.TemplateResponse(request=request,name="issue.html",
        context={
            "title": "Issue • IssueFlow",
            "css_files": list_css_files,
            "js_files": list_js_files,
        },
    )


@router.get("/register")
async def register(request: Request):
    list_js_files = ["register"]
    list_css_files = ["register", "base"]
    return templates.TemplateResponse(request=request,name="register.html",
        context={
            "title": "Register • IssueFlow",
            "css_files": list_css_files,
            "js_files": list_js_files,
        },
    )


@router.get("/login")
async def login(request: Request):
    list_js_files = ["login"]
    list_css_files = ["login", "base"]
    return templates.TemplateResponse(request=request,name="login.html",
        context={
            "title": "Login • IssueFlow",
            "css_files": list_css_files,
            "js_files": list_js_files,
        },
    )


@router.get("/profile")
async def profile(request: Request):
    list_js_files = ["profile"]
    list_css_files = ["profile", "base"]
    return templates.TemplateResponse(request=request, name="profile.html",
        context={
            "title": "Profile • IssueFlow",
            "css_files": list_css_files,
            "js_files": list_js_files,
        },
    )


@router.get("/verify-email")
async def verify_email(request: Request, user: CurrentUser):
    if user.email_verified_at:
        return RedirectResponse("/projects")

    list_js_files = ["verify_email"]
    list_css_files = ["verify_email", "base"]
    return templates.TemplateResponse(request=request, name="verify_email.html",
        context={
            "title": "Verify-Email • IssueFlow",
            "verify_url": "dd45512@yandex.ru",
            "username": "dappes",
            "email": "dd4512@yandex.ru",
            "css_files": list_css_files,
            "js_files": list_js_files,
        },
    )