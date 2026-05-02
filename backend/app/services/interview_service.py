from uuid import UUID
from app.repositories.interview_repo import InterviewRepository
from app.models.interview import (
    InterviewCreate,
    InterviewResponse,
    InterviewFilter,
    InterviewFilterResponse,
)


class InterviewService:
    def __init__(self, interview_repo: InterviewRepository):
        self.interview_repo = interview_repo

    async def create_interview(
        self, interview_data: InterviewCreate
    ) -> InterviewResponse:
        created = await self.interview_repo.create_interview(interview_data)
        return created

    async def get_interview_by_id(self, interview_id: UUID) -> InterviewResponse:
        interview = await self.interview_repo.get_interview_by_id(interview_id)
        return interview

    async def filter_interviews(
        self, filters: InterviewFilter
    ) -> InterviewFilterResponse:
        result = await self.interview_repo.filter_interviews(filters)
        return result
