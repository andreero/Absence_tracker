from django.contrib.auth import get_user_model
from .forms import SignUpForm, LoginForm
from django.views.generic import CreateView, DetailView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import UserPassesTestMixin


# Create your views here.
class SignUpView(UserPassesTestMixin, CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('accounts:users')
    template_name = 'accounts/signup.html'
    model = get_user_model()

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm


class ProfileView(DetailView):
    model = get_user_model()
    template_name = 'accounts/user_profile.html'
    context_object_name = 'profile'
    slug_url_kwarg = 'username'
    slug_field = 'username'


class ProfileListView(ListView):
    model = get_user_model()
    template_name = 'accounts/users_list.html'
    context_object_name = 'profiles'
