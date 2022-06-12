from django.contrib.auth import get_user_model
from .forms import SignUpForm, LoginForm
from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView


# Create your views here.
class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/signup.html'
    model = get_user_model()

    def form_valid(self, form):
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm


class ProfileView(DetailView):
    model = get_user_model()
    template_name = 'accounts/user_profile.html'
    context_object_name = 'profile'
    slug_url_kwarg = 'username'
    slug_field = 'username'