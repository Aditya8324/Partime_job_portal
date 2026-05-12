from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services import job_service
import schemas

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=list[schemas.JobRead])
def get_jobs(db: Session = Depends(get_db)):
    return job_service.get_all_jobs(db)


@router.post("", response_model=schemas.JobRead, status_code=201)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    return job_service.create_job(db, job)
