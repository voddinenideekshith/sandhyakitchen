from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models.brand import Brand
from models.schemas import BrandOut
from sqlalchemy import select

router = APIRouter()


@router.get("/", response_model=List[BrandOut])
async def list_brands(session: AsyncSession = Depends(get_session)):
    q = select(Brand)
    res = await session.execute(q)
    brands = res.scalars().all()
    return brands
