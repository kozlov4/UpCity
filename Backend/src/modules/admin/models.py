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
from src.core.base import Base


class Admin(Base):
    __tablename__ = "app_admin"

    admin_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    surname = Column(String(100))
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255))
