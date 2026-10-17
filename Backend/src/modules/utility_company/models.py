from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.base import Base

if TYPE_CHECKING:
    from src.modules.application.models import Application


class UtilityCompany(Base):
    __tablename__ = "utility_company"

    ut_company_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    address: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    rating: Mapped[int] = mapped_column(default=0)

    applications: Mapped[List["Application"]] = relationship(
        back_populates="utility_company"
    )
