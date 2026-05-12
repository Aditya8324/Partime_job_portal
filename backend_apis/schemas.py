from typing import Optional

from pydantic import BaseModel,Field


class JobBase(BaseModel):
    title: str
    company: str
    location: str


class EducationEntry(BaseModel):
    institute: Optional[str] = None
    board_or_university: Optional[str] = None
    degree: Optional[str] = None
    specialization: Optional[str] = None
    year: Optional[str] = None
    marks: Optional[str] = None


class EducationDetails(BaseModel):
    tenth: Optional[EducationEntry] = None
    twelfth: Optional[EducationEntry] = None
    bachelors: Optional[EducationEntry] = None
    masters: Optional[EducationEntry] = None


class resumeBase(BaseModel):
    name: str
    email: str
    phone: str
    skills: str
    experience: str
    education: Optional[EducationDetails] = None
    summary: str


class resumeCreate(resumeBase):
    pass


class resumeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[EducationDetails] = None
    summary: Optional[str] = None


class resumeRead(resumeBase):
    id: int

    class Config:
        from_attributes = True


class JobCreate(JobBase):
    pass


class JobRead(JobBase):
    id: int

    class Config:
        from_attributes = True


class SendOtpRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+?\d{10,15}$")


class VerifyOtpRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+?\d{10,15}$")
    otp: str = Field(..., min_length=6, max_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    id: int
    phone: str
    user_type: str
    full_name: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    status: str

    class Config:
        from_attributes = True
