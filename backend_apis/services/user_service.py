from sqlalchemy.orm import Session

import models


def get_or_create_user_by_phone(db: Session, phone: str, user_type: str = "worker"):
    user = db.query(models.User).filter(models.User.phone == phone).first()
    if user is None:
        user = models.User(phone=phone, user_type=user_type)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()
