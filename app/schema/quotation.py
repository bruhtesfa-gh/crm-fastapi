from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models import QuotationStatus


class QuotationLineItem(BaseModel):
    id: int
    description: str
    quantity: int
    price: float


class QuotationLineItemBase(BaseModel):
    description: str
    quantity: int
    price: float


class QuotationLineItemCreate(QuotationLineItemBase):
    pass


class QuotationLineItemUpdate(BaseModel):
    id: int
    description: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None


class QuotationBase(BaseModel):
    lead_id: int
    status: Optional[str] = None
    total_price: Optional[float] = 0.0


class QuotationCreate(BaseModel):
    lead_id: int
    line_items: List[QuotationLineItemCreate]


class QuotationUpdate(BaseModel):
    line_items: List[QuotationLineItemUpdate]


class QuotationUpdateStatus(BaseModel):
    status: QuotationStatus


class QuotationOut(QuotationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    line_items: List[QuotationLineItem]

    class Config:
        from_attributes = True


class QuotationPagination(BaseModel):
    items: List[QuotationOut]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool


class QuotationFilters(BaseModel):
    lead_id: int | None = None
    status: QuotationStatus | None = None
    price_from: float | None = None
    price_to: float | None = None


# You can also define a schema for QuotationLineItem if needed
