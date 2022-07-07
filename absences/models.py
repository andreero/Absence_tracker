import datetime
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.shortcuts import reverse
from django_softdelete.models import SoftDeleteModel


# Create your models here.
class AbsenceType(models.Model):
    absence_type = models.IntegerField(db_column='ABS_TYP_COD', primary_key=True)
    description = models.CharField(max_length=255, db_column='ABS_TYP_DSC')
    user_selection_flag = models.BooleanField(default=True, db_column='USR_SLC_FLG')

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'R_ABS_TYP'


class ApprovalStatus(models.IntegerChoices):
    NOT_APPROVED = 0
    IN_PROGRESS = 1
    APPROVED = 2
    REJECTED = 3


# class ApprovalStatus(models.Model):
#     status_code = models.IntegerField(primary_key=True, db_column='APR_STS_COD')
#     description = models.CharField(max_length=255, db_column='APR_STS_DSC')


class Absence(SoftDeleteModel, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='USR_EML',
                             related_name='user_absences')
    absence_id = models.AutoField(db_column='ABS_BCK_COD', primary_key=True)
    start_date = models.DateField(db_column='ABS_STR_DAT')
    end_date = models.DateField(db_column='ABS_END_DAT')
    absence_type = models.ForeignKey(AbsenceType, on_delete=models.CASCADE, db_column='ABS_TYP_COD',
                                     limit_choices_to={'user_selection_flag': True})
    user_comment = models.TextField(db_column='ABS_USR_MSG', blank=True)
    approval_status_code = models.PositiveSmallIntegerField(
        choices=ApprovalStatus.choices, default=ApprovalStatus.NOT_APPROVED, db_column='APR_STS_COD')
    approval_message = models.TextField(db_column='APR_MSG', default='', null=True, blank=True)
    approval_comment = models.TextField(db_column='APR_CMT', default='', null=True, blank=True)

    is_deleted = models.BooleanField(default=False, db_column='T_REC_DLT_FLG')
    created_at = models.DateTimeField(auto_now_add=True, db_column='T_REC_INS_TST')
    updated_at = models.DateTimeField(auto_now=True, db_column='T_REC_UPD_TST')
    deleted_at = models.DateTimeField(db_column='T_REC_SRC_TST', null=True, blank=True)

    def __str__(self):
        deleted = '<deleted> ' if self.is_deleted else ''
        return f'{deleted}{self.user.description} ({self.user.username}) absence from {self.start_date} to {self.end_date}'

    def is_editable_by_user(self):
        return self.approval_status_code == ApprovalStatus.NOT_APPROVED

    def get_absolute_url(self):
        return reverse('absences:absence', kwargs={'pk': self.absence_id})

    @property
    def duration(self):
        return (self.end_date - self.start_date + timedelta(days=1)).days

    def get_duration_during_year(self, year):
        if self.end_date.year < year or self.start_date.year > year:
            return 0
        else:
            return (min(self.end_date, datetime.date(year, 12, 31)) - max(self.start_date, datetime.date(year, 1, 1))
                    + timedelta(days=1)).days

    def update_approval_message_and_comment(self):
        """ Combine statuses and comments from individual approval steps into a single message and comment"""
        approval_message = list()
        approval_comment = list()
        for flow in self.approval_flow_statuses.all():
            if self.approval_status_code == ApprovalStatus.NOT_APPROVED:
                msg = f'Not yet approved by {flow.approval_flow.approver}'
            else:
                msg = f'{flow.get_approval_status_code_display()} by {flow.approval_flow.approver} on {flow.updated_at.date()}'
            approval_message.append(msg)
            print(flow, msg)
            if flow.approval_comment:
                approval_comment.append(f'{flow.approval_flow.approver}: {flow.approval_comment}')
        self.approval_message = '; '.join(approval_message)
        self.approval_comment = '; '.join(approval_comment)

    def save(self, *args, **kwargs):
        created = not self.pk  # Status objects are created only on the initial save
        self.update_approval_message_and_comment()
        super().save(*args, **kwargs)
        if created:
            for flow in self.user.requester_flows.all():
                AbsenceApprovalFlowStatus.objects.create(
                    user=self.user, absence=self, approval_flow=flow,
                    approval_comment='', approval_status_code=ApprovalStatus.NOT_APPROVED)

    class Meta:
        db_table = 'D_ABS_CLD_STS'


class ApprovalFlow(SoftDeleteModel, models.Model):
    requester = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE, db_column='USR_EML', related_name='requester_flows')
    approval_step = models.PositiveSmallIntegerField(db_column='APR_STP')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE, db_column='APR_USR_EML', related_name='approver_flows')
    notification_email_list = models.EmailField(db_column='NTF_EML_LST', null=True, blank=True)

    is_deleted = models.BooleanField(default=False, db_column='T_REC_DLT_FLG')
    created_at = models.DateTimeField(auto_now_add=True, db_column='T_REC_INS_TST')
    updated_at = models.DateTimeField(auto_now=True, db_column='T_REC_UPD_TST')
    deleted_at = models.DateTimeField(db_column='T_REC_SRC_TST', null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['requester', 'approval_step'],
                                    condition=Q(is_deleted=False), name='unique_approval_flow'),
        ]

    def __str__(self):
        deleted = '<deleted> ' if self.is_deleted else ''
        return f'{deleted}approval step #{self.approval_step} for {self.requester} by approver {self.approver}'


class AbsenceApprovalFlowStatus(SoftDeleteModel, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='USR_EML')
    absence = models.ForeignKey(
        Absence, on_delete=models.CASCADE, db_column='ABS_BCK_COD', related_name='approval_flow_statuses')
    approval_flow = models.ForeignKey(ApprovalFlow, on_delete=models.CASCADE, db_column='APR_FLW',
                                      related_name='approval_flow_statuses')
    approval_status_code = models.PositiveSmallIntegerField(
        choices=ApprovalStatus.choices, default=ApprovalStatus.NOT_APPROVED, db_column='APR_STS_COD')
    approval_comment = models.TextField(db_column='APR_CMT', blank=True)

    is_deleted = models.BooleanField(default=False, db_column='T_REC_DLT_FLG')
    created_at = models.DateTimeField(auto_now_add=True, db_column='T_REC_INS_TST')
    updated_at = models.DateTimeField(auto_now=True, db_column='T_REC_UPD_TST')
    deleted_at = models.DateTimeField(db_column='T_REC_SRC_TST', null=True, blank=True)

    def __str__(self):
        deleted = '<deleted> ' if self.is_deleted else ''
        return f'{deleted}approval flow status [{self.approval_flow}] for absence [{self.absence}], ' \
               f'status {self.approval_status_code}'

    def reject(self, approval_comment):
        self.approval_status_code = ApprovalStatus.REJECTED
        self.approval_comment = approval_comment
        self.save()

        self.absence.approval_status_code = ApprovalStatus.REJECTED
        self.absence.save()

        current_step_number = self.approval_flow.approval_step
        following_approval_flow_steps = self.absence.approval_flow_statuses\
            .filter(approval_flow__approval_step__gt=current_step_number)
        for following_flow_step in following_approval_flow_steps:
            following_flow_step.approval_status_code = ApprovalStatus.REJECTED
            following_flow_step.save()

    def approve(self, approval_comment):
        self.approval_status_code = ApprovalStatus.APPROVED
        self.approval_comment = approval_comment
        self.save()

        current_step_number = self.approval_flow.approval_step
        previous_approval_flow_steps = self.absence.approval_flow_statuses\
            .filter(approval_flow__approval_step__lt=current_step_number)

        for previous_flow_step in previous_approval_flow_steps:
            previous_flow_step.approval_status_code = ApprovalStatus.APPROVED
            previous_flow_step.save()

        following_approval_flow_steps = self.absence.approval_flow_statuses\
            .filter(approval_flow__approval_step__gt=current_step_number)
        
        if following_approval_flow_steps.exists():
            has_rejected_following_steps = following_approval_flow_steps.filter(
                approval_status_code=ApprovalStatus.REJECTED).exists()
            if has_rejected_following_steps:
                self.absence.approval_status_code = ApprovalStatus.REJECTED
            else:
                self.absence.approval_status_code = ApprovalStatus.IN_PROGRESS
        else:
            self.absence.approval_status_code = ApprovalStatus.APPROVED
        self.absence.save()
