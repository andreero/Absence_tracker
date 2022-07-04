from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import UpdateView, CreateView, DetailView, ListView
from .models import Absence, ApprovalStatus, AbsenceApprovalFlowStatus, ApprovalFlow
from django.db.models import Prefetch
import datetime
from django.db.models import Q
import calendar
from collections import namedtuple
from django.contrib.auth import get_user_model
from .filters import CalendarFilter
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import ApprovalFlowFormset


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
    fields = ['start_date', 'end_date', 'absence_type', 'user_comment']
    template_name = 'absences/absence_request_form.html'

    def form_valid(self, form):
        if not self.request.user.is_anonymous:
            form.instance.user = self.request.user
        return super().form_valid(form)


class AbsenceRequestEditView(LoginRequiredMixin, UpdateView):
    model = Absence
    fields = ['start_date', 'end_date', 'absence_type', 'user_comment']
    template_name = 'absences/absence_edit_form.html'


class AbsenceView(LoginRequiredMixin, DetailView):
    model = Absence
    template_name = 'absences/absence.html'
    context_object_name = 'absence'

    def get_object(self, queryset=None):
        absence = super().get_object(queryset=queryset)
        return absence

    def get_absence_approval_flow_status(self, absence):
        approval_flow_status = absence.approval_flow_statuses.filter(approval_flow__approver=self.request.user).first()
        return approval_flow_status

    def get(self, request, *args, **kwargs):
        absence = self.get_object()
        context = {self.context_object_name: absence}
        current_approval_flow = self.get_absence_approval_flow_status(absence=absence)
        if current_approval_flow:
            context['current_approval_flow'] = current_approval_flow
        return render(request, template_name=self.template_name,
                      context=context)


class AbsenceResolveView(LoginRequiredMixin, View):
    model = AbsenceApprovalFlowStatus
    template_name = 'absences/absence.html'

    def post(self, request, *args, **kwargs):
        approval_flow_status = self.model.objects.get(pk=self.kwargs.get('pk'))
        if request.method == 'POST' and 'approve' in request.POST:
            approval_flow_status.approve()
        if request.method == 'POST' and 'reject' in request.POST:
            approval_flow_status.reject()
        return redirect(approval_flow_status.absence)


class PendingAbsenceRequestsView(LoginRequiredMixin, ListView):
    model = Absence
    template_name = 'absences/pending_requests.html'

    def get_queryset(self):
        queryset = AbsenceApprovalFlowStatus.objects.filter(
            approval_status_code=0, approval_flow__approver=self.request.user).order_by('created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pending_requests = self.get_queryset()
        context['pending_requests'] = pending_requests
        return context


class ApprovalFlowEditView(UserPassesTestMixin, UpdateView):
    model = get_user_model()
    template_name = 'absences/approval_flow_edit_form.html'
    fields = ['username', ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ApprovalFlowFormset(self.request.POST, instance=self.object)
        else:
            context['formset'] = ApprovalFlowFormset(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if form.is_valid() and formset.is_valid():
            for setform in formset:
                if setform.cleaned_data and 'requester' not in setform.cleaned_data:
                    setform.instance = self.object
                    setform.cleaned_data['requester'] = self.object
            formset.save()
            form.save()
        else:
            return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def test_func(self):
        return self.request.user.is_superuser


class CalendarYearlyView(LoginRequiredMixin, ListView):
    model = get_user_model()
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

        current_user_absences = self.model.objects.filter(
            username=self.request.user.username
        ).prefetch_related(
            Prefetch('user_absences', queryset=all_yearly_absences_queryset))

        other_users_absences = self.model.objects.filter(
            ~Q(username=self.request.user.username)
        ).prefetch_related(
            Prefetch('user_absences', queryset=other_users_absences_queryset))

        all_user_absences_queryset = current_user_absences | other_users_absences
        filtered_queryset = CalendarFilter(self.request.GET, queryset=all_user_absences_queryset).qs
        return filtered_queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = self.object_list
        year = self.kwargs.get('year', datetime.datetime.today().year)
        context['year'] = year
        context['months'] = get_month_names_and_lengths(year=year)
        context['filter'] = CalendarFilter(self.request.GET, queryset=self.model.objects.all())
        return context


class CalendarMonthlyView(LoginRequiredMixin, ListView):
    model = get_user_model()
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

        current_user_absences = self.model.objects.filter(
            username=self.request.user.username
        ).prefetch_related(
            Prefetch('user_absences', queryset=all_yearly_absences_queryset))

        other_users_absences = self.model.objects.filter(
            ~Q(username=self.request.user.username)
        ).prefetch_related(
            Prefetch('user_absences', queryset=other_users_absences_queryset))

        all_user_absences_queryset = current_user_absences | other_users_absences
        filtered_queryset = CalendarFilter(self.request.GET, queryset=all_user_absences_queryset).qs
        return filtered_queryset

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
        context['filter'] = CalendarFilter(self.request.GET, queryset=self.model.objects.all())
        return context
