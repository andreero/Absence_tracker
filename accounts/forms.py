from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.forms import CharField


class SignUpForm(UserCreationForm):
    class Meta:
        fields = ('username', 'password1', 'password2', 'description', 'is_superuser')
        model = get_user_model()

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        return username


class LoginForm(AuthenticationForm):
    username = CharField(label='Email / Username')

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        return username
