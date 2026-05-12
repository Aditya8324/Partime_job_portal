from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, LargeBinary, String

from database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)


class User(Base):
    __tablename__ = "users"

    # Identity
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, nullable=False, index=True)
    user_type = Column(String, nullable=False, default="worker")
    full_name = Column(String, nullable=True)
    city = Column(String, nullable=True)
    email = Column(String, nullable=True)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Resume PDF storage
    resume_pdf = Column(LargeBinary, nullable=True)
    resume_source = Column(String, nullable=True)        # "uploaded" or "generated"
    resume_updated_at = Column(DateTime, nullable=True)

    # Resume form data (for generated resumes)
    skills = Column(String, nullable=True)
    experience = Column(String, nullable=True)
    education = Column(JSON, nullable=True)
    summary = Column(String, nullable=True)
