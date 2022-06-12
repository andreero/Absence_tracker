from django.urls import path
from . import views

app_name = 'absences'

urlpatterns = [
    path('request_absence/', views.AbsenceRequestView.as_view(), name='request_absence'),
    path('pending/', views.PendingAbsenceRequestsView.as_view(), name='pending_absence_requests'),
    path('absence/<str:pk>/resolve/', views.AbsenceResolveView.as_view(), name='absence_resolve'),
    path('absence/<str:pk>/edit/', views.AbsenceRequestEditView.as_view(), name='absence_edit'),
    path('absence/<str:pk>/', views.AbsenceView.as_view(), name='absence'),
    path('calendar/<int:year>/<int:month>/', views.CalendarMonthlyView.as_view(), name='calendar_monthly'),
    path('calendar/<int:year>/', views.CalendarYearlyView.as_view(), name='calendar_yearly'),
    path('calendar/', views.CalendarYearlyView.as_view(), name='calendar'),
    path('', views.IndexView.as_view(), name='index'),
]
