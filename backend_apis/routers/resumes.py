from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from services import resume_service
from services.resume_parser import parse_resume
import schemas

router = APIRouter(prefix="/resume", tags=["Resumes"])


@router.get("/me")
def get_my_resume(current_user=Depends(get_current_user)):
    return {
        "has_resume": current_user.resume_pdf is not None,
        "source": current_user.resume_source,
        "updated_at": current_user.resume_updated_at,
        "name": current_user.full_name,
        "phone": current_user.phone,
        "email": current_user.email,
        "skills": current_user.skills,
        "experience": current_user.experience,
        "education": current_user.education,
        "summary": current_user.summary,
    }


@router.post("", status_code=201)
def generate_resume(
    resume: schemas.resumeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = resume_service.generate_resume(db, resume, current_user)

    filename = f"{(user.full_name or 'resume').replace(' ', '_')}_resume.pdf"
    return Response(
        content=user.resume_pdf,
        media_type="application/pdf",
        status_code=201,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.post("/upload", status_code=201)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed",
        )

    file_bytes = file.file.read()

    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large (max 5 MB)",
        )

    parsed_data = parse_resume(file_bytes)
    resume_service.upload_resume(db, file_bytes, current_user, parsed_data)

    return {
        "message": "Resume uploaded successfully",
        "source": "uploaded",
        "parsed": parsed_data,
    }


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    deleted = resume_service.delete_resume(db, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="No resume to delete")
    return None


@router.get("/download")
def download_resume(current_user=Depends(get_current_user)):
    if current_user.resume_pdf is None:
        raise HTTPException(status_code=404, detail="No resume yet")

    name = current_user.full_name or "resume"
    filename = f"{name.replace(' ', '_')}_resume.pdf"
    return Response(
        content=current_user.resume_pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
