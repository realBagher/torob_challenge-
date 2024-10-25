from django import forms


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        label="Enter OTP",
        widget=forms.TextInput(
            attrs={"placeholder": "Enter the OTP you received", "class": "form-control"}
        ),
    )

    def clean_otp(self):
        otp = self.cleaned_data.get("otp")
        if not otp.isdigit():
            raise forms.ValidationError("OTP must be numeric.")
        if len(otp) != 6:
            raise forms.ValidationError("OTP must be 6 digits.")
        return otp
