from django import forms


class OTPEmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": " لطفا ایمیل  خود را جهت ارسال کد وارد نمایید  "}
        ),
        label="ایمیل",
    )


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        label="کد  OTP",
        widget=forms.TextInput(
            attrs={"placeholder": "لطفا کد OTP را وارد کنید ", "class": "form-control"}
        ),
    )

    def clean_otp(self):
        otp = self.cleaned_data.get("otp")
        if not otp.isdigit():
            raise forms.ValidationError("OTP must be numeric.")
        if len(otp) != 6:
            raise forms.ValidationError("OTP must be 6 digits.")
        return otp
