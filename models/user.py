import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    fullname = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    role = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
