import secrets

from redis_client import redis_client
import config


def generate_otp() -> str:
    upper = 10 ** config.OTP_LENGTH
    return f"{secrets.randbelow(upper):0{config.OTP_LENGTH}d}"


def _otp_key(phone: str) -> str:
    return f"otp:{phone}"


def _attempts_key(phone: str) -> str:
    return f"otp_attempts:{phone}"


def store_otp(phone: str, otp: str) -> None:
    redis_client.setex(_otp_key(phone), config.OTP_EXPIRE_SECONDS, otp)
    redis_client.delete(_attempts_key(phone))


def verify_otp(phone: str, otp_input: str) -> bool:
    stored = redis_client.get(_otp_key(phone))
    if stored is None:
        return False

    attempts = redis_client.incr(_attempts_key(phone))
    redis_client.expire(_attempts_key(phone), config.OTP_EXPIRE_SECONDS)

    if attempts > config.OTP_MAX_ATTEMPTS:
        redis_client.delete(_otp_key(phone))
        redis_client.delete(_attempts_key(phone))
        return False

    if stored == otp_input:
        redis_client.delete(_otp_key(phone))
        redis_client.delete(_attempts_key(phone))
        return True

    return False
