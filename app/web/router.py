from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/")
async def index():
    return FileResponse("app/web/templates/index.html")


@router.get("/login")
async def login():
    return FileResponse("app/web/templates/login.html")


@router.get("/projects")
async def projects():
    return FileResponse("app/web/templates/projects.html")


@router.get("/register")
async def register():
    return FileResponse("app/web/templates/register.html")

@router.get("/profile")
async def profile():
    return FileResponse("app/web/templates/profile.html")

@router.get("/projects/{project_id}")
async def projects(project_id: UUID):
    return FileResponse("app/web/templates/project.html")

@router.get("/projects/{project_id}/issues/{issue_id}")
async def issue(project_id: UUID, issue_id: UUID):
    return FileResponse("app/web/templates/issue.html")