from uuid import UUID
from fastapi import status
from app.repositories.interview_repo import InterviewRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.user_repo import UserRepository
from app.models.interview import (
    InterviewCreate,
    InterviewResponse,
    InterviewFilter,
    InterviewFilterResponse,
)
from app.core.exceptions import AppError


class InterviewService:
    def __init__(self, interview_repo: InterviewRepository, candidate_repo: CandidateRepository, user_repo: UserRepository):
        self.interview_repo = interview_repo
        self.candidate_repo = candidate_repo
        self.user_repo = user_repo

    async def create_interview(
        self, interview_data: InterviewCreate
    ) -> InterviewResponse:
        candidate = await self.candidate_repo.get_candidate_by_id(interview_data.candidate_id)
        if not candidate:
            raise AppError("Candidate with given ID not found", status.HTTP_400_BAD_REQUEST)
        tech_spec = await self.user_repo.get_user_by_id(interview_data.tech_spec_id)
        if not tech_spec:
            raise AppError("Tech spec with given ID not found", status.HTTP_400_BAD_REQUEST)
        created = await self.interview_repo.create_interview(interview_data)
        return created

    async def get_interview_by_id(self, interview_id: UUID) -> InterviewResponse:
        interview = await self.interview_repo.get_interview_by_id(interview_id)
        if interview is None:
            raise AppError("Interview with given ID not found", status.HTTP_404_NOT_FOUND)
        return interview

    async def filter_interviews(
        self, filters: InterviewFilter
    ) -> InterviewFilterResponse:
        result = await self.interview_repo.filter_interviews(filters)
        return result
