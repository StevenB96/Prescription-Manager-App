from django import forms


class RegisterForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=255, required=True)
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput, required=True)


class LoginForm(forms.Form):
    username = forms.EmailField(label="Email", max_length=255, required=True)
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput, required=True)


class AuthoriseForm(forms.Form):
    client_id = forms.CharField()
    redirect_uri = forms.URLField()
    response_type = forms.CharField(required=False, initial="code")
    scope = forms.CharField(required=False)
    state = forms.CharField(required=False)


class AccessGrantForm(forms.Form):
    grant_type = forms.CharField(widget=forms.HiddenInput)
    client_id = forms.CharField(widget=forms.HiddenInput)
    client_secret = forms.CharField(widget=forms.HiddenInput)
    code = forms.CharField(widget=forms.HiddenInput, required=False)
    refresh_token = forms.CharField(widget=forms.HiddenInput, required=False)
    redirect_uri = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean(self):
        cleaned_data = super().clean()
        grant_type = cleaned_data.get("grant_type")
        code = cleaned_data.get("code")
        refresh_token = cleaned_data.get("refresh_token")

        if grant_type == "authorization_code":
            if not code:
                raise forms.ValidationError(
                    "Authorization code is required for this grant type.")
            if not cleaned_data.get("redirect_uri"):
                raise forms.ValidationError(
                    "Redirect URI is required for authorization code grant.")
        elif grant_type == "refresh_token":
            if not refresh_token:
                raise forms.ValidationError(
                    "Refresh token is required for this grant type.")
        else:
            raise forms.ValidationError(
                "Invalid grant type. Must be 'authorization_code' or 'refresh_token'.")

        return cleaned_data


class RevokeTokenForm(forms.Form):
    client_id = forms.CharField(widget=forms.HiddenInput)
    client_secret = forms.CharField(widget=forms.HiddenInput)
    token = forms.CharField(widget=forms.HiddenInput)


class DeauthoriseForm(forms.Form):
    client_id = forms.CharField(widget=forms.HiddenInput())
