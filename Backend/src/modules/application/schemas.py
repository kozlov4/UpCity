# Modules/Application/schemas.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from src.modules.users.schemas import ImageOut
from src.modules.utility_company.schemas import ShowUtilityCompanyID


class ReportOut(BaseModel):
    report_id: int
    execution_date: datetime
    image: Optional[ImageOut] = None
    model_config = {"from_attributes": True}


class ShowApp(BaseModel):
    application_id: int
    name: str
    status: str
    application_date: datetime
    application_number: int
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    utility_company: ShowUtilityCompanyID
    image: Optional[ImageOut] = None
    report: Optional[ReportOut] = None
    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    user_id: int
    name: str
    surname: str
    model_config = {"from_attributes": True}


class ApplicationReview(BaseModel):
    application_id: int
    application_number: int
    name: str
    address: str
    utility_company: ShowUtilityCompanyID
    description: str
    status: str
    application_date: datetime
    user_rating: Optional[float] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    image: Optional[ImageOut] = None
    user: Optional[UserOut] = None
    report: Optional[ReportOut] = None
    model_config = {"from_attributes": True}


class CreateApp(BaseModel):
    name: str
    application_date: datetime
    application_number: int
    utility_company: ShowUtilityCompanyID
    model_config = {"from_attributes": True}
