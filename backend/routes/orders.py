from fastapi import APIRouter, HTTPException, Depends
from models.schemas import OrderCreate, OrderOut
from services.order_service import create_order
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models.order import Order as OrderModel, OrderItem

router = APIRouter()


@router.post("/", status_code=201)
async def post_order(payload: OrderCreate, session: AsyncSession = Depends(get_session)):
    try:
        res = await create_order(session, payload)
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{order_id}")
async def get_order(order_id: int, session: AsyncSession = Depends(get_session)):
    # eagerly load related order items to avoid lazy-load IO in async context
    q = select(OrderModel).options(selectinload(OrderModel.items).selectinload(OrderItem.menu_item)).where(OrderModel.id == order_id)
    r = await session.execute(q)
    order = r.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    # build response
    items = [ {"menu_item_id": it.menu_item_id, "quantity": it.quantity, "price": it.price} for it in order.items ]
    return {"id": order.id, "brand_id": order.brand_id, "total": order.total, "status": order.status, "created_at": order.created_at.isoformat(), "items": items}
