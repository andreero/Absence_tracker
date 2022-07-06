from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm
from django.forms.models import inlineformset_factory

from .models import ApprovalFlow, Absence, ApprovalStatus


class AbsenceRequestForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('end_date') < cleaned_data.get('start_date'):
            raise ValidationError(
                'End date cannot be before start date.'
            )

        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        absence_primary_key = self.instance.absence_id
        absence_overlap = Absence.objects.filter(
            user=self.request.user,
            start_date__lte=end_date,
            end_date__gte=start_date,
            approval_status_code__lt=ApprovalStatus.REJECTED
        ).exclude(absence_id=absence_primary_key).first()
        if absence_overlap:
            raise ValidationError(
                f'You already have an overlapping absence: {absence_overlap}'
            )
        return cleaned_data

    class Meta:
        model = Absence
        fields = ['start_date', 'end_date', 'absence_type', 'user_comment']


class ApprovalFlowForm(Form):
    class Meta:
        model = ApprovalFlow


ApprovalFlowFormset = inlineformset_factory(
    get_user_model(),
    ApprovalFlow,
    fk_name='requester',
    fields=('approval_step', 'approver'),
    extra=2,
    can_delete=True,
)
