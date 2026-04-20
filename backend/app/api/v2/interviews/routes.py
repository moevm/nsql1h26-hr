from fastapi import APIRouter, Depends, status, Query
from neo4j import AsyncDriver
from typing import Annotated
from uuid import UUID

from app.core.database import get_db
from app.repositories.interview_repo import InterviewRepository
from app.services.interview_service import InterviewService
from app.models.interview import (
    InterviewCreate,
    InterviewResponse,
    InterviewFilter,
    InterviewFilterResponse,
)
from app.core.security import require_role

router = APIRouter()


def get_interview_service(driver: AsyncDriver = Depends(get_db)) -> InterviewService:
    interview_repo = InterviewRepository(driver)
    return InterviewService(interview_repo)


@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    interview_data: InterviewCreate,
    interview_service: InterviewService = Depends(get_interview_service),
    current_user: dict = Depends(require_role('HR'))
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
