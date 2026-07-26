from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


router = APIRouter()


templates = Jinja2Templates(directory="app/web/templates")


@router.get("/")
async def index(request: Request):
    list_js_files = ["index"]
    list_css_files = ["index", "base"]
    return templates.TemplateResponse(request=request, name="index2.html",
        context={
            "title": "IssueFlow",
            "css_files": list_css_files,
            "js_files": list_js_files,
        })

@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(request=request,name="login.html",
        context={
            "username": "Daniel",
            "age": 30,
        })

@router.get("/projects")
async def projects(request: Request):
    return templates.TemplateResponse(request=request, name="projects.html",
        context={
            "username": "Daniel",
            "age": 30,
        })

@router.get("/register")
async def register(request: Request):
    return templates.TemplateResponse(request=request, name="register.html",
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

@router.get("/projects/{project_id}")
async def project(request: Request, project_id: UUID):
    return templates.TemplateResponse(request=request, name="project.html",
        context={
            "username": "Daniel",
            "age": 30,
        })

@router.get("/projects/{project_id}/issues/{issue_id}")
async def issue(request: Request, project_id: UUID, issue_id: UUID):
    return templates.TemplateResponse(request=request, name="issue.html",
        context={
            "username": "Daniel",
            "age": 30,
        })