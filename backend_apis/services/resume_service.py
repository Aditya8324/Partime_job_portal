from datetime import datetime

from sqlalchemy.orm import Session

import schemas
from services import pdf_service


def upload_resume(db: Session, file_bytes: bytes, current_user, parsed_data: dict = None):
    current_user.resume_pdf = file_bytes
    current_user.resume_source = "uploaded"
    current_user.resume_updated_at = datetime.utcnow()

    if parsed_data:
        # Only fill empty user fields — don't overwrite what user has already set
        if parsed_data.get("name") and not current_user.full_name:
            current_user.full_name = parsed_data["name"]
        if parsed_data.get("email") and not current_user.email:
            current_user.email = parsed_data["email"]

        # Resume-specific fields: always update from latest parse
        skills_list = parsed_data.get("skills") or []
        if skills_list:
            current_user.skills = ", ".join(s.title() for s in skills_list)

        years = parsed_data.get("experience_years")
        if years and years > 0:
            current_user.experience = f"{years} years"

    db.commit()
    db.refresh(current_user)
    return current_user


def generate_resume(db: Session, data: schemas.resumeCreate, current_user):
    current_user.full_name = data.name
    current_user.email = data.email
    current_user.skills = data.skills
    current_user.experience = data.experience
    current_user.education = data.education.model_dump() if data.education else None
    current_user.summary = data.summary

    current_user.resume_pdf = pdf_service.generate_resume_pdf(current_user)
    current_user.resume_source = "generated"
    current_user.resume_updated_at = datetime.utcnow()

    db.commit()
    db.refresh(current_user)
    return current_user


def delete_resume(db: Session, current_user):
    if current_user.resume_pdf is None:
        return False
    current_user.resume_pdf = None
    current_user.resume_source = None
    current_user.resume_updated_at = None
    db.commit()
    return True
