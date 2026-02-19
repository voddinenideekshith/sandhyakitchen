from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from database import get_session
from models.order import Order, OrderItem
from models.brand import Brand
from models.schemas import AdminOrderOut, OrderItemOut, OrderStatusUpdate
from auth import require_admin

router = APIRouter()

VALID_STATUSES = {"pending", "confirmed", "preparing", "ready", "delivered", "cancelled"}


@router.get("/", response_model=list[AdminOrderOut])
async def list_orders(_=Depends(require_admin), session: AsyncSession = Depends(get_session)):
    q = select(Order).options(selectinload(Order.items).selectinload(OrderItem.menu_item)).order_by(Order.created_at.desc())
    res = await session.execute(q)
    orders = res.scalars().all()

    out = []
    for o in orders:
        items = []
        for it in o.items:
            name = None
            if getattr(it, 'menu_item', None):
                name = getattr(it.menu_item, 'name', None)
            items.append(OrderItemOut(id=it.id, menu_item_id=it.menu_item_id, quantity=it.quantity, price=float(it.price), name=name))
        out.append(AdminOrderOut(id=o.id, brand_id=o.brand_id, total=float(o.total), status=o.status, created_at=o.created_at, items=items))
    return out


@router.patch("/{order_id}/status")
async def update_status(order_id: int, payload: OrderStatusUpdate, _=Depends(require_admin), session: AsyncSession = Depends(get_session)):
    new_status = payload.status
    if new_status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="invalid status")
    q = select(Order).where(Order.id == order_id).options(selectinload(Order.items))
    res = await session.execute(q)
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    order.status = new_status
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return {"detail": "status updated", "status": order.status}


@router.get("/stats")
async def orders_stats(_=Depends(require_admin), session: AsyncSession = Depends(get_session)):
    # total_orders, total_revenue, pending_count, preparing_count, delivered_count
    q_total = select(func.count(Order.id))
    q_revenue = select(func.coalesce(func.sum(Order.total), 0))
    r_total = await session.execute(q_total)
    total_orders = r_total.scalar_one()
    r_rev = await session.execute(q_revenue)
    total_revenue = float(r_rev.scalar_one() or 0)

    def status_count(status_name):
        q = select(func.count(Order.id)).where(Order.status == status_name)
        r = session.execute(q)
        return r

    # run counts
    pending_q = await session.execute(select(func.count(Order.id)).where(Order.status == 'pending'))
    preparing_q = await session.execute(select(func.count(Order.id)).where(Order.status == 'preparing'))
    delivered_q = await session.execute(select(func.count(Order.id)).where(Order.status == 'delivered'))

    pending_count = pending_q.scalar_one()
    preparing_count = preparing_q.scalar_one()
    delivered_count = delivered_q.scalar_one()

    return {
        "total_orders": int(total_orders),
        "total_revenue": total_revenue,
        "pending_count": int(pending_count),
        "preparing_count": int(preparing_count),
        "delivered_count": int(delivered_count),
    }
