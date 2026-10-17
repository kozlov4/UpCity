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
from src.core.base import Base


class UtilityCompany(Base):
    __tablename__ = "utility_company"

    ut_company_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    address = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=False, default=0)

    applications = relationship("Application", back_populates="utility_company")
