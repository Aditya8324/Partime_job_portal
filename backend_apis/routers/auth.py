from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from services import auth_service, otp_service, sms_service, user_service
import schemas

router = APIRouter(prefix="/auth", tags=["Auth"])

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    user_id = auth_service.decode_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = user_service.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


@router.post("/send-otp")
def send_otp(data: schemas.SendOtpRequest):
    otp = otp_service.generate_otp()
    otp_service.store_otp(data.phone, otp)
    sms_service.send_otp_sms(data.phone, otp)
    return {"message": "OTP sent"}


@router.post("/verify-otp", response_model=schemas.Token)
def verify_otp(data: schemas.VerifyOtpRequest, db: Session = Depends(get_db)):
    if not otp_service.verify_otp(data.phone, data.otp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    user = user_service.get_or_create_user_by_phone(db, data.phone)
    token = auth_service.create_access_token(user.id)
    return schemas.Token(access_token=token)


@router.get("/me", response_model=schemas.UserRead)
def get_me(current_user=Depends(get_current_user)):
    return current_user
