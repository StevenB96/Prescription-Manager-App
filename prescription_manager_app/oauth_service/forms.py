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


class TokenForm(forms.Form):
    grant_type = forms.ChoiceField(choices=[
        ("authorization_code", "authorization_code"),
        ("refresh_token", "refresh_token"),
    ])
    code = forms.CharField(required=False)
    redirect_uri = forms.URLField(required=False)
    refresh_token = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    password = forms.CharField(required=False)


class RevokeForm(forms.Form):
    token = forms.CharField()
    client_id = forms.CharField()
    client_secret = forms.CharField()


class DeauthoriseForm(forms.Form):
    client_id = forms.CharField(widget=forms.HiddenInput())
