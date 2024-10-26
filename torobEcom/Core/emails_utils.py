from django.core.mail import send_mail


def send_otp_email(user, otp_code):
    """
    Send an OTP email to the user's registered email.
    """
    subject = "Your OTP Code"
    message = f"Your OTP code is {otp_code}. It is valid for 5 minutes."
    from_email = "myapp.test.host@gmail.com"
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
