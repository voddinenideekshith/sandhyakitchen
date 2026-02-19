from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models.brand import Brand
from models.menu_item import MenuItem
from models.schemas import MenuItemOut
from sqlalchemy import select

router = APIRouter()


@router.get("/{brand_id}")
async def get_menu(brand_id: int, session: AsyncSession = Depends(get_session)):
    q = select(Brand).where(Brand.id == brand_id)
    res = await session.execute(q)
    brand = res.scalars().first()
    if not brand:
        # try by slug
        q2 = select(Brand).where(Brand.slug == str(brand_id))
        r2 = await session.execute(q2)
        brand = r2.scalars().first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    qmi = select(MenuItem).where(MenuItem.brand_id == brand.id, MenuItem.available == True)
    rmi = await session.execute(qmi)
    items = rmi.scalars().all()
    return {"brand": brand.name, "slug": brand.slug, "menu": [MenuItemOut.from_orm(i) for i in items]}
