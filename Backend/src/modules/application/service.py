import asyncio
from datetime import UTC, date, datetime
from typing import Literal

import httpx
from fastapi import HTTPException, UploadFile
from repository.email_utils import send_email
from repository.image_rep import upload
from repository.sorting_rep import sorting_user_applications
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from src.core.models import Application, Report, User, UtilityCompany


async def get_all(
    db: AsyncSession,
    sort_by_name: Literal["А-Я", "Я-А"] | None,
    sort_by_date: Literal["За зростанням", "За спаданням"] | None,
    sort_by_status: (
        Literal["В роботі", "Виконано", "Не розглянута", "Відхилено"] | None
    ),
):
    query = select(Application).options(
        joinedload(Application.image), joinedload(Application.utility_company)
    )
    query = sorting_user_applications(query, sort_by_name, sort_by_date, sort_by_status)
    query = query.order_by(desc(Application.application_date))

    result = await db.execute(query)
    return result.scalars().all()


async def get_by_id(app_id: int, db: AsyncSession):
    query = (
        select(Application)
        .options(
            joinedload(Application.image),
            joinedload(Application.utility_company),
            joinedload(Application.user),
        )
        .where(Application.application_id == app_id)
    )
    result = await db.execute(query)
    application = result.scalars().first()

    if not application:
        raise HTTPException(status_code=404, detail="Заявку не знайдено")
    return application


async def get_all_by_user(
    db: AsyncSession,
    current_user: dict,
    sort_by_name: str | None,
    sort_by_date: str | None,
    sort_by_status: str | None,
):
    if current_user["role"] not in ["user", "company"]:
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401, detail="Не вдалося витягти ідентифікатор користувача"
        )

    query = select(Application).options(
        joinedload(Application.image), joinedload(Application.utility_company)
    )
    query = sorting_user_applications(query, sort_by_name, sort_by_date, sort_by_status)

    if current_user["role"] == "company":
        query = query.where(Application.ut_company_id == int(user_id))
    else:
        query = query.where(Application.user_id == int(user_id))

    query = query.order_by(desc(Application.application_date))
    result = await db.execute(query)
    return result.scalars().all()


async def geocode_address(address: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json"}
    headers = {"User-Agent": "UpCityApp/1.0 (contact@example.com)"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, params=params, headers=headers, timeout=10.0
            )
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Geocoding request failed: {e!s}")

    if response.status_code != 200:
        raise HTTPException(
            status_code=502, detail=f"Geocoding error: {response.status_code}"
        )

    try:
        data = response.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Geocoding JSON error")

    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])

    raise HTTPException(
        status_code=400, detail="Адресу не знайдено. Перевірте правильність написання."
    )


async def create_app(
    name: str,
    address: str,
    description: str,
    company_name: str,
    photo: UploadFile,
    db: AsyncSession,
    current_user: dict,
):
    if not (3 <= len(name.strip()) <= 60):
        raise HTTPException(
            status_code=400, detail="Назва повинна містити від 3 до 60 символів"
        )
    if not (8 <= len(address.strip()) <= 100):
        raise HTTPException(
            status_code=400, detail="Адреса повинна містити від 8 до 100 символів"
        )
    if not (10 <= len(description.strip()) <= 1000):
        raise HTTPException(
            status_code=400, detail="Опис повинен містити від 10 до 1000 символів"
        )

    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    user_id = current_user.get("sub")

    user_query = (
        select(User)
        .options(joinedload(User.subscription))
        .where(User.user_id == int(user_id))
    )
    result = await db.execute(user_query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Користувач не знайдений")

    today = date.today()
    has_active_subscription = (
        user.subscription is not None
        and user.subscription.status == "Активна"
        and user.subscription.start_date <= today <= user.subscription.end_date
    )

    apps_today_query = select(func.count(Application.application_id)).where(
        Application.user_id == int(user_id),
        func.date(Application.application_date) == today,
    )
    result = await db.execute(apps_today_query)
    applications_today = result.scalar() or 0

    if not has_active_subscription and applications_today >= 3:
        raise HTTPException(
            status_code=429, detail="Ви досягли ліміту заявок на сьогодні."
        )

    comp_query = select(UtilityCompany).where(UtilityCompany.name == company_name)
    result = await db.execute(comp_query)
    company = result.scalars().first()

    if not company:
        raise HTTPException(status_code=404, detail="Компанія не знайдена")

    lat, lon = await geocode_address(address)

    upload_data = await asyncio.to_thread(upload, photo)
    image_id = upload_data["image_id"]

    num_query = (
        select(Application.application_number)
        .order_by(desc(Application.application_number))
        .limit(1)
    )
    result = await db.execute(num_query)
    max_number = result.scalar()
    new_number = (max_number + 1) if max_number else 1

    application = Application(
        name=name,
        address=address,
        description=description,
        longitude=lon,
        latitude=lat,
        status="Не розглянута",
        application_number=new_number,
        user_id=int(user_id),
        ut_company_id=company.ut_company_id,
        img_id=image_id,
        report_id=None,
    )

    db.add(application)
    await db.commit()
    await db.refresh(application)

    return {
        "message": "Заявку успішно створено",
        "application_id": application.application_id,
    }


async def complete_app(
    app_id: int,
    rating: int | None,
    status: str,
    image: UploadFile | None,
    db: AsyncSession,
    current_user: dict,
):
    if current_user["role"] != "company":
        raise HTTPException(
            status_code=403, detail="Тільки компанія може завершити заявку"
        )
    if status not in ["Виконано", "Відхилено"]:
        raise HTTPException(status_code=400, detail="Некоректний статус")

    app_query = select(Application).where(Application.application_id == app_id)
    result = await db.execute(app_query)
    application = result.scalars().first()

    if not application:
        raise HTTPException(status_code=404, detail="Заявку не знайдено")

    image_id = None
    if image and image.filename:
        uploaded_image = await asyncio.to_thread(upload, image)
        image_id = uploaded_image["image_id"]

    if application.report_id:
        rep_query = select(Report).where(Report.report_id == application.report_id)
        res = await db.execute(rep_query)
        report = res.scalars().first()
        if not report:
            raise HTTPException(status_code=500, detail="Не знайдено звіт")

        if image_id:
            report.image_id = image_id
        report.execution_date = datetime.now(UTC)
        await db.commit()
        await db.refresh(report)
    else:
        report = Report(image_id=image_id, execution_date=datetime.now(UTC))
        db.add(report)
        await db.flush()
        application.report_id = report.report_id
        await db.commit()
        await db.refresh(report)

    application.status = status
    if rating:
        application.user_rating = rating
    await db.commit()
    await db.refresh(application)

    if rating:
        user_query = select(User).where(User.user_id == application.user_id)
        res = await db.execute(user_query)
        user = res.scalars().first()
        if user:
            r_query = select(
                func.sum(Application.user_rating),
                func.count(Application.application_id),
            ).where(
                Application.user_id == user.user_id,
                Application.user_rating.is_not(None),
            )
            r_res = await db.execute(r_query)
            total_r, count_r = r_res.first()
            if count_r:
                user.rating = round(total_r / count_r, 2)
                await db.commit()

    if application.ut_company_id:
        c_query = select(func.count(Application.application_id)).where(
            Application.ut_company_id == application.ut_company_id
        )
        t_res = await db.execute(c_query)
        total_apps = t_res.scalar() or 1

        c_comp_query = select(func.count(Application.application_id)).where(
            Application.ut_company_id == application.ut_company_id,
            Application.status == "Виконано",
        )
        c_res = await db.execute(c_comp_query)
        comp_apps = c_res.scalar() or 0

        co_query = select(UtilityCompany).where(
            UtilityCompany.ut_company_id == application.ut_company_id
        )
        co_res = await db.execute(co_query)
        company = co_res.scalars().first()
        if company:
            company.rating = round((comp_apps / total_apps) * 100)
            await db.commit()

    if status == "Виконано":
        user_q = select(User).where(User.user_id == application.user_id)
        u_res = await db.execute(user_q)
        user = u_res.scalars().first()
        if user and user.email:
            name_str = (
                getattr(user, "full_name", "користувачу") or user.name or "користувачу"
            )
            subject = f"✅ Виконано: {application.name}"
            content = f"Шановний(а) {name_str},\n\nВаша заявка «{application.name}» (№{application.application_id}) була успішно виконана.\n"
            asyncio.create_task(send_email(user.email, subject, content))

    return {
        "message": "Заявку оновлено успішно",
        "application": {
            "application_id": application.application_id,
            "status": application.status,
        },
    }


async def confirm_app(app_id: int, status: str, current_user: dict, db: AsyncSession):
    if current_user["role"] not in ["company"]:
        raise HTTPException(status_code=403, detail="Недостатньо прав")
    if status != "В роботі":
        raise HTTPException(status_code=400, detail="Некоректний статус")

    query = select(Application).where(Application.application_id == app_id)
    res = await db.execute(query)
    application = res.scalars().first()

    if not application:
        raise HTTPException(status_code=404, detail="Заявку не знайдено")

    application.status = status
    await db.commit()
    await db.refresh(application)
    return {"message": "Заявку взято в роботу"}


async def destroy_app(app_id: int, current_user: dict, db: AsyncSession):
    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    user_id = int(current_user.get("sub"))
    query = select(Application).where(Application.application_id == app_id)
    res = await db.execute(query)
    application = res.scalars().first()

    if not application:
        raise HTTPException(status_code=404, detail="Заявку не знайдено")
    if application.user_id != user_id:
        raise HTTPException(status_code=403, detail="Ви не можете видалити чужу заявку")
    if application.status in ["В роботі", "Виконано", "Відхилено"]:
        raise HTTPException(
            status_code=400,
            detail=f"Неможливо видалити заявку зі статусом «{application.status}»",
        )

    await db.delete(application)
    await db.commit()
    return {"message": "Успішне видалення"}
