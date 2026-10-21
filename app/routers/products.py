from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from app.auth.jwt_handler import get_current_admin
from app.exceptions.custom_exceptions import ProductNotFoundException
from app.logger import get_logger

router = APIRouter(prefix="/api/products", tags=["Products"])
logger = get_logger(__name__)


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def add_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),  # only admins can add products
):
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    logger.info(f"Product created: {product.name} (id={product.id}) by admin {admin.id}")
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ProductNotFoundException(product_id)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    logger.info(f"Product updated: id={product_id} by admin {admin.id}")
    return product


@router.get("/{product_id}", response_model=ProductOut)
def fetch_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ProductNotFoundException(product_id)
    return product


@router.get("/", response_model=list[ProductOut])
def fetch_products(
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    search: Optional[str] = Query(None, description="Search by product name"),
    skip: int = 0,
    limit: int = Query(20, le=100),
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ProductNotFoundException(product_id)
    db.delete(product)
    db.commit()
    logger.info(f"Product deleted: id={product_id} by admin {admin.id}")
