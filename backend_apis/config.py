import os

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# OTP settings
OTP_EXPIRE_SECONDS = 300  # 5 minutes
OTP_MAX_ATTEMPTS = 5
OTP_LENGTH = 6
