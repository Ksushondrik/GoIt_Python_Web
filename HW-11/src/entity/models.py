from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy import String, Date
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), index=True)
    last_name: Mapped[str] = mapped_column(String(100), index=True)
    email: Mapped[str] = mapped_column(String(150), index=True, unique=True)
    phone: Mapped[str] = mapped_column(String(20), index=True, unique=True)
    birthday: Mapped[Date] = mapped_column(Date)
    additional_data: Mapped[str] = mapped_column(String(250))

    # @validates('phone')
    # def validate_phone(self, key, phone):
    #     if len(phone) > 20:
    #         raise ValueError("Phone number is too long")
    #     return phone
