from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderOut
from app.auth.jwt_handler import get_current_user
from app.exceptions.custom_exceptions import (
    CartEmptyException,
    InsufficientStockException,
    OrderNotFoundException,
)
from app.logger import get_logger

router = APIRouter(prefix="/api/orders", tags=["Orders"])
logger = get_logger(__name__)


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def place_order(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Places an order from everything currently in the user's cart:
    validates stock, snapshots prices, decrements inventory, clears the cart —
    all inside one DB transaction so a failure midway rolls everything back.
    """
    cart_items = (
        db.query(CartItem)
        .options(joinedload(CartItem.product))
        .filter(CartItem.user_id == current_user.id)
        .all()
    )
    if not cart_items:
        raise CartEmptyException()

    try:
        # Validate stock for every item before touching anything
        for item in cart_items:
            if item.product.stock < item.quantity:
                raise InsufficientStockException(item.product_id, item.product.stock)

        total_amount = sum(item.quantity * item.product.price for item in cart_items)
        order = Order(user_id=current_user.id, total_amount=round(total_amount, 2), status="PLACED")
        db.add(order)
        db.flush()  # get order.id before committing

        for item in cart_items:
            db.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price_at_purchase=item.product.price,
                )
            )
            item.product.stock -= item.quantity
            db.delete(item)  # clear cart

        db.commit()
        db.refresh(order)
        logger.info(f"Order placed: id={order.id} by user {current_user.id}, total={order.total_amount}")
        return order

    except Exception:
        db.rollback()
        raise


@router.get("/", response_model=list[OrderOut])
def fetch_previous_orders(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Fetch all previous orders for the logged-in user, most recent first."""
    return (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )


@router.get("/{order_id}", response_model=OrderOut)
def fetch_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if not order:
        raise OrderNotFoundException(order_id)
    return order
