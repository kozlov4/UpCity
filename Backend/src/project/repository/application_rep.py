from datetime import date, datetime
from typing import  Literal
import requests
import asyncio

from fastapi import HTTPException , UploadFile
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, asc ,desc

from project.core.models import Application, UtilityCompany, Report, User, Image
from project.repository.image_rep import upload
from project.repository.sorting_rep import sorting_user_applications
from project.repository.email_utils import send_email


def get_all(
        db:Session,
        sort_by_name:Literal["А-Я", "Я-А"] | None, 
        sort_by_date:Literal["За зростанням", "За спаданням"] | None,
        sort_by_status:Literal["В роботі", "Виконано", "Не розглянута","Відхилено"] | None
        ):
        
    query = db.query(Application)  
    
    query =  sorting_user_applications(
            query=query,
            sort_by_name=sort_by_name,
            sort_by_date=sort_by_date,
            sort_by_status=sort_by_status
        )
    
    applications = query.order_by(desc(Application.application_date)).all()
    return applications


def get_by_id(app_id:int, db:Session):
    application = db.query(Application).options(
        joinedload(Application.image),
        joinedload(Application.utility_company)
    ).filter(Application.application_id == app_id).first()

    if not application:
        raise HTTPException(status_code=404, detail="Заявку не знайдено")

    return application



def get_all_by_user(
    db: Session, 
    current_user: dict,
    sort_by_name:Literal["А-Я", "Я-А"] | None, 
    sort_by_date:Literal["За зростанням", "За спаданням"] | None,
    sort_by_status:Literal["В роботі", "Виконано", "Не розглянута" "Відхилено"] | None
    ):
    if current_user["role"] not in ["user", "company"]:
        raise HTTPException(status_code=403, detail="Недостатньо прав")
    
    user_id = current_user.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Не вдалося витягти ідентифікатор користувача")

    query = db.query(Application)  
    
    if current_user["role"] == "company":
        query =  sorting_user_applications(
            query=query,
            sort_by_name=sort_by_name,
            sort_by_date=sort_by_date,
            sort_by_status=sort_by_status
        )
        applications = query.filter(Application.ut_company_id == user_id).order_by(desc(Application.application_date))
    else:  # role == "user"
        query =  sorting_user_applications(
            query=query,
            sort_by_name=sort_by_name,
            sort_by_date=sort_by_date,
            sort_by_status=sort_by_status
        )
        
        applications = query.filter(Application.user_id == user_id).order_by(desc(Application.application_date))
        
    return applications




def create_app(name: str, address: str, description: str, company_name: str, photo: UploadFile, db: Session, current_user: dict):
    
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Назва не може бути порожньою")
    if not (3 <= len(name.strip()) <= 60):
        raise HTTPException(status_code=400, detail="Назва повинна містити від 3 до 100 символів")


    if not address or not address.strip():
        raise HTTPException(status_code=400, detail="Адреса не може бути порожньою")
    if not (8 <= len(address.strip()) <= 100):
        raise HTTPException(status_code=400, detail="Адреса повинна містити від 5 до 200 символів")


    if not description or not description.strip():
        raise HTTPException(status_code=400, detail="Опис не може бути порожнім")
    if not (10 <= len(description.strip()) <= 1000):
        raise HTTPException(status_code=400, detail="Опис повинен містити від 10 до 1000 символів")

    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Недостатньо прав")
    
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Не вдалося витягти ідентифікатор користувача")

    user = db.query(User).filter(User.user_id == user_id).outerjoin(User.subscription).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувач не знайдений")

    today = date.today()
    has_active_subscription = (
        user.subscription is not None and
        user.subscription.status == "Активна" and
        user.subscription.start_date <= today <= user.subscription.end_date
    )

    applications_today = db.query(Application).filter(
        Application.user_id == user_id,
        func.date(Application.application_date) == today
    ).count()

    if not has_active_subscription and applications_today >= 3:
        raise HTTPException(status_code=429, detail="Ви досягли ліміту заявок на сьогодні. Оформіть підписку для необмеженого доступу.")

    company = db.query(UtilityCompany).filter(UtilityCompany.name == company_name).first()
    if not company:
        raise HTTPException(status_code=404, detail="Компанія не знайдена")

    lat, lon = geocode_address(address)
    upload_data = upload(photo)
    image_id = upload_data["image_id"]

    max_number = db.query(Application.application_number).order_by(Application.application_number.desc()).first()
    new_number = (max_number[0] + 1) if max_number else 1

    application = Application(
        name=name,
        address=address,
        description=description,
        longitude=lon,
        latitude=lat,
        status="Не розглянута",
        application_number=new_number,
        user_id=user_id,
        ut_company_id=company.ut_company_id,
        img_id=image_id,
        report_id=None  # не прив'язуємо репорт
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "message": "Заявку успішно створено",
        "application_id": application.application_id
    }


def complete_app(app_id:int,rating:int,status:str, image: UploadFile, db:Session, current_user:dict ):
    if current_user["role"] != "company":
        raise HTTPException(status_code=403, detail="Тільки компанія може завершити заявку")

    application = db.query(Application).filter(Application.application_id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Заявку не знайдено")

    if status not in ["Виконано", "Відхилено"]:
        raise HTTPException(status_code=400, detail="Некоректний статус")

    image_id = None
    if image and image.filename:
        uploaded_image = upload(image)
        image_id = uploaded_image["image_id"]
        
    if application.report_id:
        report = db.query(Report).filter(Report.report_id == application.report_id).first()
        if not report:
            raise HTTPException(status_code=500, detail="Не знайдено звіт для заявки")

        if image_id:
            report.image_id = image_id
        report.execution_date = datetime.utcnow()
        db.commit()
        db.refresh(report)
    else:
        report = Report(
            image_id=image_id,
            execution_date=datetime.utcnow()
        )
        db.add(report)
        db.flush()

        application.report_id = report.report_id
        db.commit()
        db.refresh(report)

    application.status = status
    if rating:
        application.user_rating = rating
    db.commit()
    db.refresh(application)

    if rating:
        user = db.query(User).filter(User.user_id == application.user_id).first()
        if user:
            total_ratings = db.query(func.sum(Application.user_rating)).filter(
                Application.user_id == user.user_id,
                Application.user_rating.isnot(None)
            ).scalar() or 0

            rating_count = db.query(func.count(Application.application_id)).filter(
                Application.user_id == user.user_id,
                Application.user_rating.isnot(None)
            ).scalar() or 1

            user.rating = round(total_ratings / rating_count, 2)
            db.commit()

    company_id = application.ut_company_id
    if company_id:
        total_applications = db.query(func.count(Application.application_id)).filter(
            Application.ut_company_id == company_id
        ).scalar() or 1

        completed_applications = db.query(func.count(Application.application_id)).filter(
            Application.ut_company_id == company_id,
            Application.status == "Виконано"
        ).scalar() or 0

        company = db.query(UtilityCompany).filter(UtilityCompany.ut_company_id == company_id).first()
        if company:
            company.rating = round((completed_applications / total_applications) * 100)
            db.commit()

    main_image = None
    if application.img_id:
        img_obj = db.query(Image).filter(Image.image_id == application.img_id).first()
        if img_obj:
            main_image = {"image_url": img_obj.image_url}

    report_out = None
    if report and report.image_id:
        report_img_obj = db.query(Image).filter(Image.image_id == report.image_id).first()
        report_out = {
            "report_id": report.report_id,
            "execution_date": report.execution_date,
            "image": {"image_url": report_img_obj.image_url} if report_img_obj else None
        }
        
    if status == "Виконано":
        user = db.query(User).filter(User.user_id == application.user_id).first()
        if user and user.email:
            subject = f"✅ Виконано: {application.name or 'Ваша заявка'}"
            
            content = (
                f"Шановний(а) {user.full_name if 'full_name' in user.__dict__ and user.full_name else 'користувачу'},\n\n"
                f"Ми раді повідомити, що ваша заявка «{application.name}» (№{application.application_id}) була успішно виконана компанією.\n\n"
                f"Дякуємо за довіру до нашого сервісу!\n\n"
                f"З найкращими побажаннями,\n"
                f"Команда підтримки"
            )

            asyncio.create_task(send_email(user.email, subject, content))

    return {
        "message": "Заявку оновлено успішно",
        "application": {
            "application_id": application.application_id,
            "status": application.status,
            "image": main_image,
            "report": report_out,
        }
    }

def geocode_address(address: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json"}
    headers = {"User-Agent": "UpCityApp/1.0 (contact@example.com)"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Geocoding request failed: {str(e)}")

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Geocoding error: {response.status_code} - {response.text}")

    try:
        data = response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Geocoding JSON error: {str(e)}. Response was: {response.text}")

    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])

    # Якщо адреса не знайдена
    raise HTTPException(status_code=400, detail="Адресу не знайдено. Перевірте правильність написання.")



def confirm_app(app_id:int, status:str, current_user:dict, db:Session):
    if current_user["role"] not in ["company"]:
        raise HTTPException(status_code=403, detail="Недостатньо прав")
    
    application = db.query(Application).filter(Application.application_id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Заявку не знайдено")
    
    if status not in ["В роботі"]:
        raise HTTPException(status_code=400, detail="Некоректний статус")
    
    application.status = status
    db.commit()
    db.refresh(application)
    
    return {
        "message": "Заявку взято в роботу",
        "application": {
            "application_id": application.application_id,
            "status": application.status,
        }
    }
    
    
def destroy_app(
    app_id: int,
    current_user: dict,
    db: Session
):
    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    try:
        user_id = int(current_user.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Невірний ідентифікатор користувача")

    application = db.query(Application).filter(Application.application_id == app_id).first()

    if not application:
        raise HTTPException(status_code=404, detail="Заявку не знайдено")

    if application.user_id != user_id:
        raise HTTPException(status_code=403, detail="Ви не можете видалити чужу заявку")

    if application.status in ["В роботі", "Виконано", "Відхилено"]:
        raise HTTPException(
            status_code=400,
            detail=f"Неможливо видалити заявку зі статусом «{application.status}»"
        )

    db.delete(application)
    db.commit()

    return {"message": "Успішне видалення"}
