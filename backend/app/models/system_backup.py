from typing import List
from pydantic import BaseModel
from app.models.user import UserDB
from app.models.vacancy import VacancyResponse
from app.models.test_task import TestTaskResponse
from app.models.candidate import CandidateResponse
from app.models.interview import InterviewResponse
from app.models.offer import OfferResponse


class SystemBackup(BaseModel):
    users: List[UserDB]
    vacancies: List[VacancyResponse]
    test_tasks: List[TestTaskResponse]
    candidates: List[CandidateResponse]
    interviews: List[InterviewResponse]
    offers: List[OfferResponse]
