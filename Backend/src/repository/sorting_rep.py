from core import Application
from sqlalchemy import asc, desc


def sorting_user_applications(query, sort_by_name, sort_by_date, sort_by_status):
    if sort_by_name == "А-Я":
        query = query.order_by(asc(Application.name))
    elif sort_by_name == "Я-А":
        query = query.order_by(desc(Application.name))

    if sort_by_date == "За зростанням":
        query = query.order_by(asc(Application.application_date))
    elif sort_by_date == "За спаданням":
        query = query.order_by(desc(Application.application_date))

    if sort_by_status:
        query = query.filter(Application.status == sort_by_status)

    return query
