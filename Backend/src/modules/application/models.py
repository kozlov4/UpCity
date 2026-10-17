from sqlalchemy import (
    DECIMAL,
    TIMESTAMP,
    CheckConstraint,
    Column,
    Date,
    Double,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship


class Application(Base):
    __tablename__ = "application"

    application_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    address = Column(String(255))
    longitude = Column(DECIMAL(9, 6))
    latitude = Column(DECIMAL(9, 6))
    status = Column(String(50), default="В роботі")
    application_date = Column(TIMESTAMP, server_default=func.now())
    application_number = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("app_user.user_id", ondelete="CASCADE"))
    ut_company_id = Column(
        Integer, ForeignKey("utility_company.ut_company_id", ondelete="CASCADE")
    )
    img_id = Column(Integer, ForeignKey("image.image_id", ondelete="SET NULL"))
    report_id = Column(Integer, ForeignKey("report.report_id", ondelete="SET NULL"))
    user_rating = Column(Float)

    __table_args__ = (
        CheckConstraint(
            "status IN ('Не розглянута', 'В роботі', 'Виконано', 'Відхилено')",
            name="check_application_status",
        ),
    )

    user = relationship("User", back_populates="applications")
    utility_company = relationship("UtilityCompany", back_populates="applications")
    image = relationship("Image", back_populates="applications")
    report = relationship("Report", back_populates="applications")
