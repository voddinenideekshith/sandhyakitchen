from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from models.user import User
from models.schemas import Token, LoginRequest, UserOut
from database import get_session
from auth import verify_password, create_access_token, get_password_hash

router = APIRouter()


@router.post('/login', response_model=Token)
async def login(form: LoginRequest, session: AsyncSession = Depends(get_session)):
    q = select(User).where(User.username == form.username)
    res = await session.execute(q)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    if not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(data={'sub': user.username}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}


# Utility to create an admin user via API if desired (not exposed by default)
@router.post('/create-admin', response_model=UserOut)
async def create_admin(user_in: UserOut, session: AsyncSession = Depends(get_session)):
    # upsert admin user
    q = select(User).where(User.username == user_in.username)
    res = await session.execute(q)
    existing = res.scalars().first()
    if existing:
        existing.role = user_in.role
        await session.commit()
        await session.refresh(existing)
        return existing
    hashed = get_password_hash('admin')
    new = User(username=user_in.username, hashed_password=hashed, role=user_in.role)
    session.add(new)
    await session.commit()
    await session.refresh(new)
    return new
