from uuid import UUID
from app.repositories.offer_repo import OfferRepository
from app.models.offer import (
    OfferCreate,
    OfferResponse,
    OfferFilter,
    OfferFilterResponse,
)


class OfferService:
    def __init__(self, offer_repo: OfferRepository):
        self.offer_repo = offer_repo

    async def create_offer(self, offer_data: OfferCreate) -> OfferResponse:
        return await self.offer_repo.create_offer(offer_data)

    async def get_offer_by_id(self, offer_id: UUID) -> OfferResponse:
        return await self.offer_repo.get_offer_by_id(offer_id)

    async def filter_offers(self, filters: OfferFilter) -> OfferFilterResponse:
        return await self.offer_repo.filter_offers(filters)
