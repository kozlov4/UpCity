from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    ForeignKey, 
    Date, 
    Text, 
    TIMESTAMP, 
    DECIMAL, 
    CheckConstraint, 
    func, 
    Double,
    Float
) 
from sqlalchemy.orm import relationship

from project.core.database import Base


class UtilityCompany(Base):
    __tablename__ = 'utility_company'

    ut_company_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    address = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=False, default=0)

    applications = relationship("Application", back_populates="utility_company")


class Subscription(Base):
    __tablename__ = 'app_subscription'

    subscription_id = Column(Integer, primary_key=True, index=True)
    status = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)

    users = relationship("User", back_populates="subscription")

    __table_args__ = (
        CheckConstraint("status IN ('Активна', 'Неактивна', 'Скасована')", name="check_subscription_status"),
    )


class Image(Base):
    __tablename__ = 'image'

    image_id = Column(Integer, primary_key=True, index=True)
    image_url = Column(Text, nullable=False)
    image_date = Column(TIMESTAMP, server_default=func.now())

    users = relationship("User", back_populates="image")
    reports = relationship("Report", back_populates="image")
    applications = relationship("Application", back_populates="image")


class User(Base):
    __tablename__ = 'app_user'

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    surname = Column(String(100))
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255))
    rating = Column(Double, nullable= False, default=0)
    subscription_id = Column(Integer, ForeignKey("app_subscription.subscription_id", ondelete="SET NULL"))
    image_id = Column(Integer, ForeignKey("image.image_id", ondelete="SET NULL"))

    subscription = relationship("Subscription", back_populates="users")
    blocking = relationship("Blocking", back_populates="user", uselist=False)
    image = relationship("Image", back_populates="users")
    applications = relationship("Application", back_populates="user")


class Report(Base):
    __tablename__ = 'report'

    report_id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("image.image_id", ondelete="CASCADE"), nullable=True)
    execution_date = Column(TIMESTAMP, server_default=func.now())

    image = relationship("Image", back_populates="reports")
    applications = relationship("Application", back_populates="report")


class Application(Base):
    __tablename__ = 'application'

    application_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    address = Column(String(255))
    longitude = Column(DECIMAL(9, 6))
    latitude = Column(DECIMAL(9, 6))
    status = Column(String(50), default='В роботі')
    application_date = Column(TIMESTAMP, server_default=func.now())
    application_number = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("app_user.user_id", ondelete="CASCADE"))
    ut_company_id = Column(Integer, ForeignKey("utility_company.ut_company_id", ondelete="CASCADE"))
    img_id = Column(Integer, ForeignKey("image.image_id", ondelete="SET NULL"))
    report_id = Column(Integer, ForeignKey("report.report_id", ondelete="SET NULL"))
    user_rating = Column(Float)

    __table_args__ = (
        CheckConstraint("status IN ('Не розглянута', 'В роботі', 'Виконано', 'Відхилено')", name="check_application_status"),
    )

    user = relationship("User", back_populates="applications")
    utility_company = relationship("UtilityCompany", back_populates="applications")
    image = relationship("Image", back_populates="applications")
    report = relationship("Report", back_populates="applications")


class Blocking(Base):
    __tablename__ = 'blocking'

    blocking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("app_user.user_id", ondelete="CASCADE"))
    block_date = Column(TIMESTAMP, server_default=func.now())
    reason = Column(Text)

    user = relationship("User", back_populates="blocking")


class Admin(Base):
    __tablename__ = 'app_admin'

    admin_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    surname = Column(String(100))
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255))





