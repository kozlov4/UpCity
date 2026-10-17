from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.core.base import Base


class Admin(Base):
    __tablename__ = "admin"

    admin_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(100))
    surname: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[Optional[str]] = mapped_column(String(255))
