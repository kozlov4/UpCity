from core import Base
from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship


class Image(Base):
    __tablename__ = "image"

    image_id = Column(Integer, primary_key=True, index=True)
    image_url = Column(Text, nullable=False)
    image_date = Column(TIMESTAMP, server_default=func.now())

    users = relationship("User", back_populates="image")
    reports = relationship("Report", back_populates="image")
    applications = relationship("Application", back_populates="image")


class Report(Base):
    __tablename__ = "report"

    report_id = Column(Integer, primary_key=True, index=True)
    image_id = Column(
        Integer, ForeignKey("image.image_id", ondelete="CASCADE"), nullable=True
    )
    execution_date = Column(TIMESTAMP, server_default=func.now())

    image = relationship("Image", back_populates="reports")
    applications = relationship("Application", back_populates="report")


class Blocking(Base):
    __tablename__ = "blocking"

    blocking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("app_user.user_id", ondelete="CASCADE"))
    block_date = Column(TIMESTAMP, server_default=func.now())
    reason = Column(Text)

    user = relationship("User", back_populates="blocking")


class Admin(Base):
    __tablename__ = "app_admin"

    admin_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    surname = Column(String(100))
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255))
