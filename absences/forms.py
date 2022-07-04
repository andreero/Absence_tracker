from django.contrib.auth import get_user_model
from django.forms.models import inlineformset_factory
from django.forms import Form, ModelChoiceField, IntegerField, NumberInput, Select
from .models import ApprovalFlow


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
