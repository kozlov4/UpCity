from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from schemas.image_schemas import ImageOut
from schemas.utility_company_schemas import ShowUtilityCompanyID


class ReportOut(BaseModel):
    report_id: int
    execution_date: datetime
    image: Optional[ImageOut] = None


class ShowApp(BaseModel):
    application_id: int
    name: str
    status: str
    application_date: datetime
    application_number: int
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    utility_company: ShowUtilityCompanyID
    image: ImageOut
    report: Optional[ReportOut]  # додано звіт

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    user_id: int
    name: str
    surname: str


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
    image: ImageOut
    user: Optional[UserOut]
    report: Optional[ReportOut]  # додано звіт

    model_config = {"from_attributes": True}


class CreateApp(BaseModel):
    name: str
    application_date: datetime
    application_number: int
    utility_company: ShowUtilityCompanyID

    model_config = {"from_attributes": True}
