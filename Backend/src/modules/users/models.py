from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Date,
    Double,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.base import Base

if TYPE_CHECKING:
    from src.modules.application.models import Application, Image


class User(Base):
    __tablename__ = "app_user"

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(100))
    surname: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[Optional[str]] = mapped_column(String(255))
    rating: Mapped[float] = mapped_column(Double, default=0)
    subscription_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("app_subscription.subscription_id", ondelete="SET NULL")
    )
    image_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("image.image_id", ondelete="SET NULL")
    )

    subscription: Mapped[Optional["Subscription"]] = relationship(
        back_populates="users"
    )
    blocking: Mapped[Optional["Blocking"]] = relationship(
        back_populates="user", uselist=False
    )
    image: Mapped[Optional["Image"]] = relationship(back_populates="users")
    applications: Mapped[List["Application"]] = relationship(back_populates="user")


class Subscription(Base):
    __tablename__ = "app_subscription"

    subscription_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    status: Mapped[Optional[str]] = mapped_column(String(50))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)

    users: Mapped[List["User"]] = relationship(back_populates="subscription")

    __table_args__ = (
        CheckConstraint(
            "status IN ('Активна', 'Неактивна', 'Скасована')",
            name="check_subscription_status",
        ),
    )


class Blocking(Base):
    __tablename__ = "blocking"

    blocking_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("app_user.user_id", ondelete="CASCADE")
    )
    block_date: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
    reason: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped[Optional["User"]] = relationship(back_populates="blocking")
