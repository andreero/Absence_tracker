from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.forms import CharField, ModelChoiceField
from .models import Country


class SignUpForm(UserCreationForm):
    class Meta:
        fields = ('username', 'password1', 'password2', 'description', 'country_code', 'is_superuser')
        model = get_user_model()

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        return username


class ProfileEditForm(UserChangeForm):
    class Meta:
        fields = ('description', 'country_code', 'is_superuser')
        model = get_user_model()

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        return username


class LoginForm(AuthenticationForm):
    username = CharField(label='Email / Username')

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        return username
