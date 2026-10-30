from typing import Literal

from fastapi import HTTPException, status
from modules.auth.hashing import Hash
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.utility_company.models import UtilityCompany

from .schemas import AddUtilityCompany, UtilityCompanyUpdate


async def get_all(
    current_user: dict,
    db: AsyncSession,
    sort_by_rating: Literal["За зростанням", "За спаданням"] | None,
):
    if current_user["role"] not in {"admin", "user"}:
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    query = select(UtilityCompany)

    if sort_by_rating == "За зростанням":
        query = query.order_by(asc(UtilityCompany.rating))
    elif sort_by_rating == "За спаданням":
        query = query.order_by(desc(UtilityCompany.rating))

    result = await db.execute(query)
    return result.scalars().all()


async def get_one(id: int, db: AsyncSession, current_user: dict):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    query = select(UtilityCompany).where(UtilityCompany.ut_company_id == id)
    result = await db.execute(query)
    company = result.scalars().first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компанію за id = {id} не знайдено",
        )
    return company


async def create_company(
    db: AsyncSession, request: AddUtilityCompany, current_user: dict
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    query = select(UtilityCompany).where(UtilityCompany.email == request.email)
    result = await db.execute(query)
    existing_company = result.scalars().first()

    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Компанія з email = {request.email} вже існує",
        )

    new_company = UtilityCompany(
        name=request.name,
        address=request.address,
        phone=request.phone,
        email=request.email,
        password=Hash.bcrypt(request.password),
    )
    db.add(new_company)
    await db.commit()
    await db.refresh(new_company)
    return new_company


async def update(
    id: int, request: UtilityCompanyUpdate, db: AsyncSession, current_user: dict
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    query = select(UtilityCompany).where(UtilityCompany.ut_company_id == id)
    result = await db.execute(query)
    company = result.scalars().first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компанію за id = {id} не знайдено",
        )

    email_query = select(UtilityCompany).where(
        UtilityCompany.email == request.email, UtilityCompany.ut_company_id != id
    )
    email_result = await db.execute(email_query)
    existing_company = email_result.scalars().first()

    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Компанія з email = {request.email} вже існує",
        )

    company.name = request.name
    company.address = request.address
    company.phone = request.phone
    company.email = request.email
    await db.commit()
    await db.refresh(company)
    return company


async def destroy(id: int, db: AsyncSession, current_user: dict):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    query = select(UtilityCompany).where(UtilityCompany.ut_company_id == id)
    result = await db.execute(query)
    company = result.scalars().first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"КП з id = {id} не знайдено"
        )

    await db.delete(company)
    await db.commit()
