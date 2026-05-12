from sqlalchemy.orm import Session

import models
import schemas


def get_all_jobs(db: Session):
    return db.query(models.Job).all()


def create_job(db: Session, job: schemas.JobCreate):
    new_job = models.Job(**job.model_dump())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job
