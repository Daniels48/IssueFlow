from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


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
    list_css_files = ["layout", "issue", "base"]
    return templates.TemplateResponse(request=request,name="issue.html",
        context={
            "title": "Issue • IssueFlow",
            "css_files": list_css_files,
            "js_files": list_js_files,
        },
    )


@router.get("/register")
async def register(request: Request):
    return templates.TemplateResponse(request=request, name="register.html",
        context={
            "username": "Daniel",
            "age": 30,
        })


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(request=request,name="login.html",
        context={
            "username": "Daniel",
            "age": 30,
        })


@router.get("/profile")
async def profile(request: Request):
    return templates.TemplateResponse(request=request, name="profile.html",
        context={
            "username": "Daniel",
            "age": 30,
        })