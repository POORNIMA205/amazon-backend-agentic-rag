from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartItemOut, CartOut
from app.auth.jwt_handler import get_current_user
from app.exceptions.custom_exceptions import (
    ProductNotFoundException,
    InsufficientStockException,
    CartItemNotFoundException,
)
from app.logger import get_logger

router = APIRouter(prefix="/api/cart", tags=["Cart"])
logger = get_logger(__name__)


def _get_cart_items(db: Session, user_id: int):
    return (
        db.query(CartItem)
        .options(joinedload(CartItem.product))
        .filter(CartItem.user_id == user_id)
        .all()
    )


@router.post("/", response_model=CartOut, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    payload: CartItemAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise ProductNotFoundException(payload.product_id)

    item = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id, CartItem.product_id == payload.product_id)
        .first()
    )

    # Check total desired quantity (existing in cart + new) against stock,
    # not just the newly added amount.
    already_in_cart = item.quantity if item else 0
    if product.stock < already_in_cart + payload.quantity:
        raise InsufficientStockException(product.id, product.stock)

    if item:
        item.quantity += payload.quantity
    else:
        item = CartItem(
            user_id=current_user.id,
            product_id=payload.product_id,
            quantity=payload.quantity,
        )
        db.add(item)

    db.commit()
    logger.info(f"User {current_user.id} added product {payload.product_id} to cart")
    return _build_cart_response(db, current_user.id)


@router.get("/", response_model=CartOut)
def get_cart(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Fetch all items currently in the logged-in user's cart."""
    return _build_cart_response(db, current_user.id)


@router.put("/{product_id}", response_model=CartOut)
def update_cart_item(
    product_id: int,
    payload: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id, CartItem.product_id == product_id)
        .first()
    )
    if not item:
        raise CartItemNotFoundException(product_id)

    if item.product.stock < payload.quantity:
        raise InsufficientStockException(product_id, item.product.stock)

    item.quantity = payload.quantity
    db.commit()
    return _build_cart_response(db, current_user.id)


@router.delete("/{product_id}", response_model=CartOut)
def remove_from_cart(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id, CartItem.product_id == product_id)
        .first()
    )
    if not item:
        raise CartItemNotFoundException(product_id)

    db.delete(item)
    db.commit()
    logger.info(f"User {current_user.id} removed product {product_id} from cart")
    return _build_cart_response(db, current_user.id)


def _build_cart_response(db: Session, user_id: int) -> CartOut:
    items = _get_cart_items(db, user_id)
    total_items = sum(i.quantity for i in items)
    total_amount = sum(i.quantity * i.product.price for i in items)
    return CartOut(items=items, total_items=total_items, total_amount=round(total_amount, 2))
