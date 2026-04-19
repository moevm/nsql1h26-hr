from typing import List
from pydantic import BaseModel
from user import UserResponse
from vacancy import VacancyResponse
from test_task import TestTaskResponse
from candidate import CandidateResponse
from interview import InterviewResponse
from offer import OfferResponse


class SystemBackup(BaseModel):
    users: List[UserResponse]
    vacancies: List[VacancyResponse]
    test_tasks: List[TestTaskResponse]
    candidates: List[CandidateResponse]
    interviews: List[InterviewResponse]
    offers: List[OfferResponse]
