from django.contrib.auth.backends import BaseBackend
from django_redis import get_redis_connection
from .models import Customer


class OTPBackend(BaseBackend):
    def authenticate(self, request, phone_number=None, otp=None):
        if not phone_number or not otp:
            return None

        try:
            user = Customer.objects.get(phone_number=phone_number)
        except Customer.DoesNotExist:
            return None

        redis_conn = get_redis_connection("default")
        stored_otp = redis_conn.get(f"otp:{user.id}")

        if stored_otp and otp == stored_otp.decode("utf-8"):
            user.is_verified = True
            user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return Customer.objects.get(pk=user_id)
        except Customer.DoesNotExist:
            return None
