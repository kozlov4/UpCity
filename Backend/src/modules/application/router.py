from typing import Literal, Optional

from core import get_db
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from oauth2 import get_current_user
from repository import application_rep
from schemas.application_schemas import ApplicationReview, ShowApp
from sqlalchemy.orm import Session

router = APIRouter(tags=["Заявки ⚠️"], prefix="/application")


@router.get("/", response_model=list[ShowApp], status_code=status.HTTP_200_OK)
def get_applications_for_all_users(
    db: Session = Depends(get_db),
    sort_by_name: Literal["А-Я", "Я-А"] | None = Query(
        None, description="Сортування за алфавітом по імені"
    ),
    sort_by_date: Literal["За зростанням", "За спаданням"] | None = Query(
        None, description="Сортування за датою"
    ),
    sort_by_status: (
        Literal["В роботі", "Виконано", "Не розглянута", "Відхилено"] | None
    ) = Query(None, description="Фільтрація за статусом"),
):
    return application_rep.get_all(
        db=db,
        sort_by_name=sort_by_name,
        sort_by_date=sort_by_date,
        sort_by_status=sort_by_status,
    )


@router.get(
    "/all_by_user/", response_model=list[ShowApp], status_code=status.HTTP_200_OK
)
def get_all_applications_by_user(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    sort_by_name: Literal["А-Я", "Я-А"] | None = Query(
        None, description="Сортування за алфавітом по імені"
    ),
    sort_by_date: Literal["За зростанням", "За спаданням"] | None = Query(
        None, description="Сортування за датою"
    ),
    sort_by_status: (
        Literal["В роботі", "Виконано", "Не розглянута", "Відхилено"] | None
    ) = Query(None, description="Фільтрація за статусом"),
):
    return application_rep.get_all_by_user(
        db=db,
        current_user=current_user,
        sort_by_name=sort_by_name,
        sort_by_date=sort_by_date,
        sort_by_status=sort_by_status,
    )


@router.get(
    "/{app_id}/", status_code=status.HTTP_200_OK, response_model=ApplicationReview
)
def application_review(
    app_id: int,
    db: Session = Depends(get_db),
):
    return application_rep.get_by_id(
        app_id=app_id,
        db=db,
    )


@router.post("/create/")
async def create_application(
    name: str = Form(...),
    address: str = Form(...),
    description: str = Form(...),
    company_name: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return application_rep.create_app(
        name=name,
        address=address,
        description=description,
        company_name=company_name,
        photo=photo,
        db=db,
        current_user=current_user,
    )


@router.put("/{app_id}/complete", status_code=200)
async def complete_application(
    app_id: int,
    rating: Optional[int] = Form(None),
    status: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return application_rep.complete_app(
        app_id=app_id,
        rating=rating,
        status=status,
        image=image,
        db=db,
        current_user=current_user,
    )


@router.put("/{app_id}/confirm/", status_code=200)
async def confirm_application(
    app_id: int,
    status: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return application_rep.confirm_app(
        app_id=app_id, status=status, current_user=current_user, db=db
    )


@router.delete("/{app_id}/", status_code=200)
async def delete_application(
    app_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return application_rep.destroy_app(app_id=app_id, current_user=current_user, db=db)
