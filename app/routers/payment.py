import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order, Payment
from app.models.user import User
from app.schemas.order import PaymentCreate, PaymentOut
from app.auth.jwt_handler import get_current_user
from app.exceptions.custom_exceptions import OrderNotFoundException, PaymentFailedException
from app.logger import get_logger

router = APIRouter(prefix="/api/payment", tags=["Payment"])
logger = get_logger(__name__)


@router.post("/", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def process_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mock payment gateway. In production this would call out to
    Razorpay/Stripe/PayPal and verify a webhook instead of trusting
    the client-supplied result.
    """
    order = (
        db.query(Order)
        .filter(Order.id == payload.order_id, Order.user_id == current_user.id)
        .first()
    )
    if not order:
        raise OrderNotFoundException(payload.order_id)

    if payload.simulate_failure:
        order.status = "FAILED"
        db.commit()
        logger.warning(f"Payment failed (simulated) for order {order.id}")
        raise PaymentFailedException("Payment declined by gateway (simulated).")

    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        method=payload.method,
        status="SUCCESS",
        transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
    )
    order.status = "PAID"
    db.add(payment)
    db.commit()
    db.refresh(payment)

    logger.info(f"Payment success for order {order.id}: txn={payment.transaction_id}")
    return payment


@router.get("/{order_id}", response_model=PaymentOut)
def get_payment_for_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if not order or not order.payment:
        raise OrderNotFoundException(order_id)
    return order.payment
