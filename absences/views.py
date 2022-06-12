from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import UpdateView, CreateView, DetailView, ListView
from .models import Absence, ApprovalStatus
from .forms import AbsenceRequestForm
from accounts.models import User
from django.db.models import Prefetch
import datetime
from django.db.models import Q
import calendar
from collections import namedtuple


def get_month_names_and_lengths(year):
    month_tuple = namedtuple('Month', ['index', 'title', 'num_days'])
    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    month_names_and_lengths = [
        month_tuple(month, month_names[month], calendar.monthrange(year, month)[1]) for month in range(1, 13)
    ]
    return month_names_and_lengths


def get_last_day_of_month(year, month):
    return calendar.monthrange(year, month)[1]


def prev_month(year, month):
    if month == 1:
        return year-1, 12
    else:
        return year, month-1


def next_month(year, month):
    if month == 12:
        return year+1, 1
    else:
        return year, month+1



# Create your views here.
class IndexView(View):
    def get(self, request):
        return render(request, template_name='absences/index.html')


class AbsenceRequestView(LoginRequiredMixin, CreateView):
    model = Absence
    fields = ['start_date', 'end_date', 'user_comment']
    template_name = 'absences/absence_request_form.html'

    def form_valid(self, form):
        if not self.request.user.is_anonymous:
            form.instance.user = self.request.user
        return super().form_valid(form)


class AbsenceRequestEditView(LoginRequiredMixin, UpdateView):
    model = Absence
    fields = ['start_date', 'end_date', 'user_comment']
    template_name = 'absences/absence_edit_form.html'

    def get_initial(self):
        initial = super().get_initial()
        print(initial)
        return initial


class AbsenceView(LoginRequiredMixin, DetailView):
    model = Absence
    template_name = 'absences/absence.html'
    context_object_name = 'absence'

    def get_object(self, queryset=None):
        absence = super().get_object(queryset=queryset)
        return absence

    def get(self, request, *args, **kwargs):
        absence = self.get_object()
        return render(request, template_name=self.template_name, context={self.context_object_name: absence})


class AbsenceResolveView(LoginRequiredMixin, View):
    model = Absence
    template_name = 'absences/absence.html'

    def post(self, request, *args, **kwargs):
        absence = self.model.objects.get(pk=self.kwargs.get('pk'))
        if request.method == 'POST' and 'approve' in request.POST:
            absence.approve()
        if request.method == 'POST' and 'reject' in request.POST:
            absence.reject()
        return redirect(absence)


class PendingAbsenceRequestsView(LoginRequiredMixin, ListView):
    model = Absence
    template_name = 'absences/pending_requests.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_requests'] = Absence.objects.filter(approval_status_code=0).order_by('created_at')
        return context


class CalendarYearlyView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'absences/yearly_calendar.html'

    def get_queryset(self):
        year = self.kwargs.get('year', datetime.datetime.today().year)
        year_start = datetime.date(year, 1, 1)
        year_end = datetime.date(year, 12, 31)

        all_yearly_absences_queryset = Absence.objects.filter(
                start_date__lte=year_end,
                end_date__gte=year_start,
            )

        approved_yearly_absences_queryset = Absence.objects.filter(
                start_date__lte=year_end,
                end_date__gte=year_start,
                approval_status_code=ApprovalStatus.APPROVED
            )

        if self.request.user.is_superuser:
            # Select all absences that happen to fall on that year
            other_users_absences_queryset = all_yearly_absences_queryset
        else:
            # Select absences that happen to fall on that year, but only approved absences are selected for other users
            other_users_absences_queryset = approved_yearly_absences_queryset

        current_user_absences = User.objects.filter(
            username=self.request.user.username
        ).prefetch_related(
            Prefetch('user_absences', queryset=all_yearly_absences_queryset))

        other_users_absences = User.objects.filter(
            ~Q(username=self.request.user.username)
        ).prefetch_related(
            Prefetch('user_absences', queryset=other_users_absences_queryset))
        return list(current_user_absences) + list(other_users_absences)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = self.object_list
        year = self.kwargs.get('year', datetime.datetime.today().year)
        context['year'] = year
        context['months'] = get_month_names_and_lengths(year=year)
        return context


class CalendarMonthlyView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'absences/monthly_calendar.html'

    def get_queryset(self):
        year = self.kwargs.get('year', datetime.datetime.today().year)
        month = self.kwargs.get('month', datetime.datetime.today().month)
        month_start = datetime.date(year, month, 1)
        month_end = datetime.date(year, month, get_last_day_of_month(year=year, month=month))

        all_yearly_absences_queryset = Absence.objects.filter(
            start_date__lte=month_end,
            end_date__gte=month_start,
        )

        approved_yearly_absences_queryset = Absence.objects.filter(
            start_date__lte=month_end,
            end_date__gte=month_start,
            approval_status_code=ApprovalStatus.APPROVED
        )

        if self.request.user.is_superuser:
            # Select all absences that happen to fall on that year
            other_users_absences_queryset = all_yearly_absences_queryset
        else:
            # Select absences that happen to fall on that year, but only approved absences are selected for other users
            other_users_absences_queryset = approved_yearly_absences_queryset

        current_user_absences = User.objects.filter(
            username=self.request.user.username
        ).prefetch_related(
            Prefetch('user_absences', queryset=all_yearly_absences_queryset))

        other_users_absences = User.objects.filter(
            ~Q(username=self.request.user.username)
        ).prefetch_related(
            Prefetch('user_absences', queryset=other_users_absences_queryset))
        return list(current_user_absences) + list(other_users_absences)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = self.object_list
        year = self.kwargs.get('year', datetime.datetime.today().year)
        month = self.kwargs.get('month', datetime.datetime.today().month)
        context['year'] = year
        context['days'] = list(range(1, get_last_day_of_month(year=year, month=month)+1))

        next_month_year, next_month_month = next_month(year, month)
        prev_month_year, prev_month_month = prev_month(year, month)
        context['next_month'] = {
            'month': next_month_month,
            'year': next_month_year,
            'title': datetime.date(next_month_year, next_month_month, 1).strftime('%B %Y')
        }
        context['prev_month'] = {
            'month': prev_month_month,
            'year': prev_month_year,
            'title': datetime.date(prev_month_year, prev_month_month, 1).strftime('%B %Y')
        }
        return context
