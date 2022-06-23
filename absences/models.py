from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from datetime import timedelta
from django_softdelete.models import SoftDeleteModel


# Create your models here.
class AbsenceType(models.Model):
    pass


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
        return f'{self.user.description} ({self.user.username}) absence from {self.start_date} to {self.end_date}'

    def is_editable_by_user(self):
        return self.approval_status_code == ApprovalStatus.NOT_APPROVED

    def get_absolute_url(self):
        return reverse('absences:absence', kwargs={'pk': self.absence_id})

    def get_duration(self):
        return (self.end_date - self.start_date + timedelta(days=1)).days

    def approve(self):
        self.approval_status_code = ApprovalStatus.APPROVED
        self.save()

    def reject(self):
        self.approval_status_code = ApprovalStatus.REJECTED
        self.save()


class ApprovalFlow(SoftDeleteModel, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='USR_EML')
    approval_step = models.PositiveSmallIntegerField(db_column='APR_STP')
    approval_user_email = models.EmailField(db_column='APR_USR_EML')
    notification_email_list = models.EmailField(db_column='NTF_EML_LST')

    is_deleted = models.BooleanField(default=False, db_column='T_REC_DLT_FLG')
    created_at = models.DateTimeField(auto_now_add=True, db_column='T_REC_INS_TST')
    updated_at = models.DateTimeField(auto_now=True, db_column='T_REC_UPD_TST')
    deleted_at = models.DateTimeField(db_column='T_REC_SRC_TST')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'approval_step'], name='unique_approval_flow'),
        ]


class AbsenceApprovalFlowStatus(SoftDeleteModel, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='USR_EML')
    absence = models.ForeignKey(ApprovalFlow, on_delete=models.CASCADE)
    approval_status_code = models.PositiveSmallIntegerField(
        choices=ApprovalStatus.choices, default=ApprovalStatus.NOT_APPROVED, db_column='APR_STS_COD')
    approval_comment = models.TextField(db_column='APR_CMT')
