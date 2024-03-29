from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.forms import CharField


class SignUpForm(UserCreationForm):
    class Meta:
        fields = ('username', 'user_id', 'password1', 'password2', 'description', 'groups', 'date_joined', 'absence_limit', 'country_code', 'is_superuser')
        model = get_user_model()

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        return username


class ProfileEditForm(UserChangeForm):
    class Meta:
        fields = ('username', 'user_id', 'description', 'groups', 'date_joined', 'absence_limit', 'country_code', 'is_superuser')
        model = get_user_model()

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        return username


class LoginForm(AuthenticationForm):
    username = CharField(label='Email / Username')

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        return username
