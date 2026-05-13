from fastapi import APIRouter, Depends, status, Query
from neo4j import AsyncDriver
from typing import Annotated
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.repositories.interview_repo import InterviewRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.user_repo import UserRepository
from app.services.interview_service import InterviewService
from app.models.interview import (
    InterviewCreate,
    InterviewResponse,
    InterviewFilter,
    InterviewFilterResponse,
    InterviewPatch,
    InterviewUpdate
)
from app.core.security import require_role

router = APIRouter()


def get_interview_service(driver: AsyncDriver = Depends(get_db)) -> InterviewService:
    candidate_repo = CandidateRepository(driver)
    user_repo = UserRepository(driver)
    interview_repo = InterviewRepository(driver)
    return InterviewService(interview_repo, candidate_repo,user_repo)


@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    interview_data: InterviewCreate,
    interview_service: InterviewService = Depends(get_interview_service),
    _: dict = Depends(require_role("HR")),
):
    return await interview_service.create_interview(interview_data)


@router.get(
    "/{interview_id}", response_model=InterviewResponse, status_code=status.HTTP_200_OK
)
async def get_interview_by_id(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
):
    return await interview_service.get_interview_by_id(interview_id)


@router.get("", response_model=InterviewFilterResponse, status_code=status.HTTP_200_OK)
async def filter_interviews(
    filters: Annotated[InterviewFilter, Query()],
    interview_service: InterviewService = Depends(get_interview_service),
):
    return await interview_service.filter_interviews(filters)


@router.patch(
    "/{interview_id}", response_model=InterviewResponse, status_code=status.HTTP_200_OK
)
async def patch_interview(
    interview_id: UUID,
    patch_data: InterviewPatch,
    interview_service: InterviewService = Depends(get_interview_service),
    _: dict = Depends(require_role("TECH_SPEC")),
    current_user: dict = Depends(get_current_user),
):
    interview = await interview_service.patch_interview(interview_id, patch_data, current_user)
    return interview
    
@router.patch("/{interview_id}/admin", response_model=InterviewResponse, status_code=status.HTTP_200_OK)
async def admin_update_interview(
    interview_id: UUID,
    update_data: InterviewUpdate,
    interview_service: InterviewService = Depends(get_interview_service),
    _: dict = Depends(require_role("HR")),  # HR или ADMIN
):
    return await interview_service.update_interview(interview_id, update_data)
