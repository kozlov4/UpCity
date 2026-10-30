from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

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
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    address: Mapped[str | None] = mapped_column(String(255))
    longitude: Mapped[Decimal | None] = mapped_column(DECIMAL(9, 6))
    latitude: Mapped[Decimal | None] = mapped_column(DECIMAL(9, 6))
    status: Mapped[str | None] = mapped_column(String(50), default="В роботі")
    application_date: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )

    # ИСПРАВЛЕНО: добавлено mapped_column()
    application_number: Mapped[int] = mapped_column()
    user_rating: Mapped[float | None] = mapped_column(default=None)

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE")
    )
    ut_company_id: Mapped[int | None] = mapped_column(
        ForeignKey("utility_company.ut_company_id", ondelete="CASCADE")
    )
    img_id: Mapped[int | None] = mapped_column(
        ForeignKey("image.image_id", ondelete="SET NULL")
    )
    report_id: Mapped[int | None] = mapped_column(
        ForeignKey("report.report_id", ondelete="SET NULL")
    )

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
    image_id: Mapped[int | None] = mapped_column(
        ForeignKey("image.image_id", ondelete="CASCADE")
    )
    execution_date: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )

    image: Mapped[Optional["Image"]] = relationship(back_populates="reports")
    applications: Mapped[list["Application"]] = relationship(back_populates="report")


class Image(Base):
    __tablename__ = "image"

    image_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    image_url: Mapped[str] = mapped_column(Text)
    image_date: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )

    users: Mapped[list["User"]] = relationship(back_populates="image")
    reports: Mapped[list["Report"]] = relationship(back_populates="image")
    applications: Mapped[list["Application"]] = relationship(back_populates="image")
