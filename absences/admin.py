from django.contrib import admin

from .models import Absence, ApprovalFlow, AbsenceApprovalFlowStatus, AbsenceType, PublicHoliday


class AbsenceAdmin(admin.ModelAdmin):
    model = Absence

    def get_queryset(self, request):
        return self.model.global_objects


class AbsenceTypeAdmin(admin.ModelAdmin):
    model = AbsenceType


class ApprovalFlowAdmin(admin.ModelAdmin):
    model = ApprovalFlow

    def get_queryset(self, request):
        return self.model.global_objects


class AbsenceApprovalFlowStatusAdmin(admin.ModelAdmin):
    model = AbsenceApprovalFlowStatus

    def get_queryset(self, request):
        return self.model.global_objects


# Register your models here.
admin.site.register(Absence, AbsenceAdmin)
admin.site.register(AbsenceType, AbsenceTypeAdmin)
admin.site.register(ApprovalFlow, ApprovalFlowAdmin)
admin.site.register(AbsenceApprovalFlowStatus, AbsenceApprovalFlowStatusAdmin)
admin.site.register(PublicHoliday)
