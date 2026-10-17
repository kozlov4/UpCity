from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    DECIMAL,
    TIMESTAMP,
    CheckConstraint,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.base import Base

if TYPE_CHECKING:
    from src.modules.users.models import User
    from src.modules.utility_company.models import UtilityCompany


class Application(Base):
    __tablename__ = "application"

    application_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    address: Mapped[Optional[str]] = mapped_column(String(255))
    longitude: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(9, 6))
    latitude: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(9, 6))
    status: Mapped[Optional[str]] = mapped_column(String(50), default="В роботі")
    application_date: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
    application_number: Mapped[int]
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("app_user.user_id", ondelete="CASCADE")
    )
    ut_company_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("utility_company.ut_company_id", ondelete="CASCADE")
    )
    img_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("image.image_id", ondelete="SET NULL")
    )
    report_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("report.report_id", ondelete="SET NULL")
    )
    user_rating: Mapped[Optional[float]]

    __table_args__ = (
        CheckConstraint(
            "status IN ('Не розглянута', 'В роботі', 'Виконано', 'Відхилено')",
            name="check_application_status",
        ),
    )

    user: Mapped[Optional["User"]] = relationship(back_populates="applications")
    utility_company: Mapped[Optional["UtilityCompany"]] = relationship(
        back_populates="applications"
    )
    image: Mapped[Optional["Image"]] = relationship(back_populates="applications")
    report: Mapped[Optional["Report"]] = relationship(back_populates="applications")


class Report(Base):
    __tablename__ = "report"

    report_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    image_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("image.image_id", ondelete="CASCADE")
    )
    execution_date: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )

    image: Mapped[Optional["Image"]] = relationship(back_populates="reports")
    applications: Mapped[List["Application"]] = relationship(back_populates="report")


class Image(Base):
    __tablename__ = "image"

    image_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    image_url: Mapped[str] = mapped_column(Text)
    image_date: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )

    users: Mapped[List["User"]] = relationship(back_populates="image")
    reports: Mapped[List["Report"]] = relationship(back_populates="image")
    applications: Mapped[List["Application"]] = relationship(back_populates="image")
