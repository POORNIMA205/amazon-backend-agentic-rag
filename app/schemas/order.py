from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.product import ProductOut


class OrderItemOut(BaseModel):
    id: int
    quantity: int
    price_at_purchase: float
    product: ProductOut

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    total_amount: float
    status: str
    created_at: datetime
    items: list[OrderItemOut]

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    order_id: int
    method: str = Field(..., pattern="^(CARD|UPI|COD|NETBANKING)$")
    # In a real system card/upi details would go through a PCI-compliant
    # gateway (Razorpay/Stripe) and never touch our own server directly.
    simulate_failure: Optional[bool] = False


class PaymentOut(BaseModel):
    id: int
    order_id: int
    amount: float
    method: str
    status: str
    transaction_id: str
    created_at: datetime

    class Config:
        from_attributes = True
