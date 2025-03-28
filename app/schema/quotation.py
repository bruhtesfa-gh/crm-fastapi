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


class QuotationLineItemUpdate(QuotationLineItemBase):
    pass


class QuotationBase(BaseModel):
    lead_id: int
    status: Optional[str] = None
    total_price: Optional[float] = 0.0


class QuotationCreate(BaseModel):
    lead_id: int
    line_items: List[QuotationLineItemCreate]


class QuotationUpdate(BaseModel):
    status: QuotationStatus


class QuotationOut(QuotationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    line_items: List[QuotationLineItem]

    class Config:
        from_attributes = True


# You can also define a schema for QuotationLineItem if needed
