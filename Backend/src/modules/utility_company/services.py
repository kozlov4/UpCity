from typing import Literal

from core import UtilityCompany
from fastapi import HTTPException, status
from hashing import Hash
from schemas.utility_company_schemas import AddUtilityCompany, UtilityCompanyUpdate
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session


def get_all(
    current_user: dict,
    db: Session,
    sort_by_rating: Literal["За зростанням", "За спаданням"] | None,
):
    if current_user["role"] != "admin" and current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Недостатньо прав")
    query = db.query(UtilityCompany)

    if sort_by_rating == "За зростанням":
        query = query.order_by(asc(UtilityCompany.rating))
    elif sort_by_rating == "За спаданням":
        query = query.order_by(desc(UtilityCompany.rating))

    return query.all()


def get_one(id, db: Session, current_user: dict):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Недостатньо прав")
    company = (
        db.query(UtilityCompany).filter(UtilityCompany.ut_company_id == id).first()
    )
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компанію за id = {id} не знайдено",
        )
    return company


def create_company(db: Session, request: AddUtilityCompany, current_user: dict):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Недостатньо прав")
    existing_company = (
        db.query(UtilityCompany).filter(UtilityCompany.email == request.email).first()
    )
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
    db.commit()
    db.refresh(new_company)
    return new_company


def update(id, request: UtilityCompanyUpdate, db: Session, current_user: dict):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Недостатньо прав")
    company = (
        db.query(UtilityCompany).filter(UtilityCompany.ut_company_id == id).first()
    )
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компанію за id = {id} не знайдено",
        )

    existing_company = (
        db.query(UtilityCompany)
        .filter(
            UtilityCompany.email == request.email, UtilityCompany.ut_company_id != id
        )
        .first()
    )
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Компанія з email = {request.email} вже існує",
        )

    company.name = request.name
    company.address = request.address
    company.phone = request.phone
    company.email = request.email
    db.commit()
    db.refresh(company)
    return company


def destroy(id, db: Session, current_user: dict):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Недостатньо прав")
    company = (
        db.query(UtilityCompany)
        .filter(UtilityCompany.ut_company_id == id)
        .delete(synchronize_session=False)
    )
    db.commit()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"КП з id = {id} не знайдено"
        )
    return
