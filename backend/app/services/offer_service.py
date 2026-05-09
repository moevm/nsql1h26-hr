from uuid import UUID
from fastapi import status
from app.repositories.offer_repo import OfferRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.vacancy_repo import VacancyRepository
from app.models.offer import (
    OfferCreate,
    OfferResponse,
    OfferFilter,
    OfferFilterResponse,
    OfferStatus
)
from app.models.candidate import CandidateStatus
from app.core.exceptions import AppError


class OfferService:
    def __init__(self, offer_repo: OfferRepository, candidate_repo: CandidateRepository, vacancy_repo: VacancyRepository):
        self.offer_repo = offer_repo
        self.candidate_repo = candidate_repo
        self.vacancy_repo = vacancy_repo

    async def create_offer(self, offer_data: OfferCreate) -> OfferResponse:
        candidate_id = offer_data.candidate_id
        if offer_data.status != OfferStatus.PENDING:
            raise AppError("New offer status must be pending", status.HTTP_400_BAD_REQUEST)
        candidate = await self.candidate_repo.get_candidate_by_id(candidate_id)
        if not candidate:
            raise AppError("Candidate not found", status.HTTP_400_BAD_REQUEST)
        if candidate["status"] != CandidateStatus.INTERVIEW_PASSED:
            raise AppError("Candidate's status must be INTERVIEW_PASSED", status.HTTP_400_BAD_REQUEST)
        vacancy = await self.vacancy_repo.get_vacancy_by_id(offer_data.vacancy_id)
        if not vacancy:
            raise AppError("Vacancy not found", status.HTTP_400_BAD_REQUEST)
        offer = await self.offer_repo.create_offer(offer_data)
        if offer:
            await self.candidate_repo.patch_candidate(candidate["id"], { "status": CandidateStatus.OFFER })
        return offer

    async def get_offer_by_id(self, offer_id: UUID) -> OfferResponse:
        offer = await self.offer_repo.get_offer_by_id(offer_id)
        if not offer:
            raise AppError("Offer not found", status.HTTP_404_NOT_FOUND)
        return offer

    async def filter_offers(self, filters: OfferFilter) -> OfferFilterResponse:
        return await self.offer_repo.filter_offers(filters)
