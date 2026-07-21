from uuid import UUID

from fastapi import APIRouter, status

from app.modules.auth.dependencies import CurrentUser
from app.modules.project_members.schema import ProjectMemberCreate, ProjectMemberResponse, ProjectMemberUpdate, \
    ProjectMemberResponse_
from app.modules.project_members.service import MemberService


router = APIRouter(prefix="/projects/{project_id}/members",tags=["Project Members"])


@router.post("",response_model=ProjectMemberResponse_,status_code=status.HTTP_201_CREATED)
async def add_member(project_id: UUID, data: ProjectMemberCreate, current_user: CurrentUser,service: MemberService):
    return await service.add_member(project_id=project_id, data=data, current_user=current_user)


@router.get("",response_model=list[ProjectMemberResponse])
async def get_members(project_id: UUID,current_user: CurrentUser,service: MemberService):
    return await service.get_members(project_id=project_id,current_user=current_user)


@router.patch("/{user_id}", response_model=ProjectMemberResponse)
async def update_member(project_id: UUID, user_id: UUID, data: ProjectMemberUpdate, current_user: CurrentUser, service: MemberService):
    return await service.update_role(project_id=project_id, user_id=user_id, data=data, current_user=current_user)


@router.delete("/{user_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(project_id: UUID,user_id: UUID,current_user: CurrentUser,service: MemberService):
    await service.delete_member(project_id=project_id,user_id=user_id,current_user=current_user)