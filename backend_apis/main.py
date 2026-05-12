from fastapi import FastAPI

from database import Base, engine
import models  # noqa: F401  (registers tables with Base)
from routers import jobs, resumes,auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Part-time Job Portal")


app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(resumes.router)


@app.get("/")
def read_root():
    return {"message": "Job portal API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
