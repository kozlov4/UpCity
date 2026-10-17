from core import Base
from sqlalchemy import (
    Column,
    Double,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "app_user"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    surname = Column(String(100))
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255))
    rating = Column(Double, nullable=False, default=0)
    subscription_id = Column(
        Integer, ForeignKey("app_subscription.subscription_id", ondelete="SET NULL")
    )
    image_id = Column(Integer, ForeignKey("image.image_id", ondelete="SET NULL"))

    subscription = relationship("Subscription", back_populates="users")
    blocking = relationship("Blocking", back_populates="user", uselist=False)
    image = relationship("Image", back_populates="users")
    applications = relationship("Application", back_populates="user")


class Subscription(Base):
    __tablename__ = "app_subscription"

    subscription_id = Column(Integer, primary_key=True, index=True)
    status = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)

    users = relationship("User", back_populates="subscription")

    __table_args__ = (
        CheckConstraint(
            "status IN ('Активна', 'Неактивна', 'Скасована')",
            name="check_subscription_status",
        ),
    )
