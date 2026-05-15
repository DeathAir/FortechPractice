import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, TIMESTAMP

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



class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    log_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    Actions = Column(Text, nullable=False)
    Target = Column(Text, nullable=False)
    Outcome = Column(Text, nullable=False)