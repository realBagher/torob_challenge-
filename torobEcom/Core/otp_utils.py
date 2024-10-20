import random
from django_redis import get_redis_connection


def generate_otp(user):
    """
    Generate a 6-digit OTP for the user and store it in Redis with a 5-minute expiry.
    """
    otp_code = random.randint(100000, 999999)
    redis_conn = get_redis_connection("default")
    redis_conn.set(f"otp:{user.id}", otp_code, ex=300)  # Store OTP for 5 minutes
    return otp_code


def verify_otp(user, otp):
    """
    Verify the OTP for the user. Returns True if OTP is valid, False otherwise.
    """
    redis_conn = get_redis_connection("default")
    stored_otp = redis_conn.get(f"otp:{user.id}")

    if stored_otp and otp == stored_otp.decode("utf-8"):
        redis_conn.delete(f"otp:{user.id}")  # OTP used, delete it
        return True
    return False
