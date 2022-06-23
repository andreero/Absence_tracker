from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.SignUpView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    # path('users/', views.CustomLoginView.as_view(), name='login'),
    path('', include('django.contrib.auth.urls')),
    path('<pk>', views.ProfileView.as_view(), name='profile'),
]
