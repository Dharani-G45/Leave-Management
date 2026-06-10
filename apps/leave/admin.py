from django.contrib import admin
from .models import LeaveRequest, LeaveApproval, LeaveBalance

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        'leave_id', 
        'applicant', 
        'applicant_type', 
        'leave_type', 
        'from_date', 
        'to_date', 
        'days', 
        'current_stage', 
        'status'
    )
    
    list_filter = ('status', 'current_stage', 'applicant_type', 'leave_type')
    
    search_fields = ('leave_id', 'applicant__username', 'reason', 'reviewer_comments')
    
    readonly_fields = ('leave_id',)
    
    fieldsets = (
        ('Request Identification', {
            'fields': ('leave_id', 'applicant', 'applicant_type')
        }),
        ('Leave Details', {
            'fields': ('leave_type', 'from_date', 'to_date', 'days', 'reason', 'doc_path')
        }),
        ('Workflow & Approvals Pipeline Matrix', {
            'fields': ('reporting_person', 'current_stage', 'status', 'reviewer_comments')
        }),
    )


@admin.register(LeaveApproval)
class LeaveApprovalAdmin(admin.ModelAdmin):
    list_display = ('leave', 'approver', 'approver_role', 'decision')
    list_filter = ('approver_role', 'decision')
    search_fields = ('leave__leave_id', 'approver__username', 'comment')


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = (
        'staff_id', 
        'year', 
        'sick_total', 'sick_used', 
        'casual_total', 'casual_used', 
        'emergency_total', 'emergency_used',
        'exam_total', 'exam_used'
    )
    list_filter = ('year',)
    search_fields = ('staff_id__username',)

# @admin.register(HolidayCalendar)
# class HolidayCalendarAdmin(admin.ModelAdmin):
#     """Allows Superadmins and HR to seeds institutional & government dates"""
#     list_display = ('title', 'holiday_type', 'start_date', 'end_date')
#     list_filter = ('holiday_type', 'start_date')
#     search_fields = ('title', 'description')