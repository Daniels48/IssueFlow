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

@router.get("/project/{project_id}")
async def project(project_id: int):
    return FileResponse("app/web/templates/project.html")

@router.get("/issue/{issue_id}")
async def project(issue_id: int):
    return FileResponse("app/web/templates/issue.html")