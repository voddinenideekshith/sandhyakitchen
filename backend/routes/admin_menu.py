from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_session
from models.menu_item import MenuItem
from models.order import OrderItem
from models.brand import Brand
from models.schemas import MenuItemOut, MenuItemCreate, MenuItemUpdate
from auth import require_admin

router = APIRouter()

# admin auth is handled by `auth.require_admin` dependency (JWT)


@router.post("/", response_model=MenuItemOut)
async def create_menu_item(payload: MenuItemCreate, _=Depends(require_admin), session: AsyncSession = Depends(get_session)):
    # ensure brand exists
    q = select(Brand).where(Brand.id == payload.brand_id)
    res = await session.execute(q)
    brand = res.scalars().first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    item = MenuItem(
        brand_id=payload.brand_id,
        name=payload.name,
        price=payload.price,
        category=payload.category,
        available=payload.available if payload.available is not None else True,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return MenuItemOut.from_orm(item)



@router.get("/", response_model=List[MenuItemOut])
async def list_all_items(brand_id: Optional[int] = None, _=Depends(require_admin), session: AsyncSession = Depends(get_session)):
    """Admin-only: list all menu items. If `brand_id` is provided, filter by brand."""
    q = select(MenuItem)
    if brand_id is not None:
        q = q.where(MenuItem.brand_id == brand_id)
    res = await session.execute(q)
    items = res.scalars().all()
    return [MenuItemOut.from_orm(i) for i in items]


@router.put("/{item_id}", response_model=MenuItemOut)
async def update_menu_item(item_id: int, payload: MenuItemUpdate, _=Depends(require_admin), session: AsyncSession = Depends(get_session)):
    q = select(MenuItem).where(MenuItem.id == item_id)
    res = await session.execute(q)
    item = res.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    if payload.name is not None:
        item.name = payload.name
    if payload.price is not None:
        item.price = payload.price
    if payload.category is not None:
        item.category = payload.category
    if payload.available is not None:
        item.available = payload.available

    session.add(item)
    await session.commit()
    await session.refresh(item)
    return MenuItemOut.from_orm(item)


@router.patch("/{item_id}/toggle", response_model=MenuItemOut)
async def toggle_menu_item(item_id: int, _=Depends(require_admin), session: AsyncSession = Depends(get_session)):
    q = select(MenuItem).where(MenuItem.id == item_id)
    res = await session.execute(q)
    item = res.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    item.available = False if item.available else True
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return MenuItemOut.from_orm(item)


@router.delete("/{item_id}")
async def delete_menu_item(item_id: int, _=Depends(require_admin), session: AsyncSession = Depends(get_session)):
    # do not allow deletion if referenced in order_items
    q_ref = select(func.count(OrderItem.id)).where(OrderItem.menu_item_id == item_id)
    res_ref = await session.execute(q_ref)
    cnt = res_ref.scalar_one()
    if cnt and cnt > 0:
        raise HTTPException(status_code=400, detail="Cannot delete menu item referenced by orders")

    q = select(MenuItem).where(MenuItem.id == item_id)
    res = await session.execute(q)
    item = res.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    # soft delete by marking unavailable
    item.available = False
    session.add(item)
    await session.commit()
    return {"detail": "deleted (soft)"}
