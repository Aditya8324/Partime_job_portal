import logging

logger = logging.getLogger("uvicorn.error")


def send_otp_sms(phone: str, otp: str) -> None:
    logger.info(f"SMS to {phone}: Your DaylyWork OTP is {otp} (valid 5 min)")
    print(f"\n{'='*60}\n[OTP] {phone}: {otp}\n{'='*60}\n")
