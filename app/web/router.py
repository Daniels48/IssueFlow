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