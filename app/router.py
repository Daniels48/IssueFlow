from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as user_router
from app.modules.projects.router import router as project_router
from app.modules.project_members.router import router as members_router
from app.modules.issue.router import router as issue_router
from app.modules.comments.router import router as comment_router

api_router = APIRouter(prefix="/api", tags=["api"])


api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(project_router)
api_router.include_router(members_router)
api_router.include_router(issue_router)
api_router.include_router(comment_router)