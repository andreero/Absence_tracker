from django import forms
from .models import Absence
from django.conf import settings


class AbsenceRequestForm(forms.ModelForm):
    class Meta():
        model = Absence
        fields = ['start_date', 'end_date', 'user_comment']
