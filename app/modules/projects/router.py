from uuid import UUID

from fastapi import APIRouter, status

from app.modules.auth.dependencies import CurrentUser
from app.modules.projects.schema import ProjectCreate, ProjectResponse, ProjectUpdate, ProjectListResponse, \
    ProjectDetailResponse
from app.modules.projects.service import project_service


router = APIRouter(prefix="/projects",tags=["Projects"])


@router.post("",response_model=ProjectResponse,status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate, current_user: CurrentUser, service: project_service):
    return await service.create(data=data, current_user=current_user)


@router.get( "", response_model=list[ProjectListResponse])
async def get_projects(current_user: CurrentUser, service: project_service):
    return await service.get_all(current_user)


@router.get("/{public_id}",response_model=ProjectDetailResponse)
async def get_project(public_id: UUID, current_user: CurrentUser, service: project_service):
    return await service.get_by_public_id(public_id, current_user)


@router.patch("/{public_id}", response_model=ProjectUpdate)
async def update_project(public_id: UUID, data: ProjectUpdate, current_user: CurrentUser, service: project_service):
    return await service.update(public_id, data, current_user)


@router.delete("/{public_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(public_id: UUID, current_user: CurrentUser, service: project_service):
    await service.delete(public_id, current_user)