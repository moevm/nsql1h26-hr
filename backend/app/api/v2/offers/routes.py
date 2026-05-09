from fastapi import APIRouter, Depends, status, Query
from neo4j import AsyncDriver
from typing import Annotated
from uuid import UUID

from app.core.database import get_db
from app.repositories.offer_repo import OfferRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.vacancy_repo import VacancyRepository
from app.services.offer_service import OfferService
from app.models.offer import (
    OfferCreate,
    OfferResponse,
    OfferFilter,
    OfferFilterResponse,
    OfferPatch
)
from app.core.security import require_role

router = APIRouter()


def get_offer_service(driver: AsyncDriver = Depends(get_db)) -> OfferService:
    offer_repo = OfferRepository(driver)
    candidate_repo = CandidateRepository(driver)
    vacancy_repo = VacancyRepository(driver)
    return OfferService(offer_repo, candidate_repo, vacancy_repo)


@router.post("", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
async def create_offer(
    offer_data: OfferCreate,
    offer_service: OfferService = Depends(get_offer_service),
    _: dict = Depends(require_role("HR")),
):
    return await offer_service.create_offer(offer_data)


@router.get("/{offer_id}", response_model=OfferResponse, status_code=status.HTTP_200_OK)
async def get_offer_by_id(
    offer_id: UUID,
    offer_service: OfferService = Depends(get_offer_service),
):
    return await offer_service.get_offer_by_id(offer_id)


@router.get("", response_model=OfferFilterResponse, status_code=status.HTTP_200_OK)
async def filter_offers(
    filters: Annotated[OfferFilter, Query()],
    offer_service: OfferService = Depends(get_offer_service),
):
    return await offer_service.filter_offers(filters)


@router.patch(
    "/{offer_id}", response_model=OfferResponse, status_code=status.HTTP_200_OK
)
async def patch_offer(
    offer_id: UUID,
    patch_data: OfferPatch,
    offer_service: OfferService = Depends(get_offer_service),
    _: dict = Depends(require_role("MANAGER")),
):
    offer = await offer_service.patch_offer(offer_id, patch_data)
    return offer
