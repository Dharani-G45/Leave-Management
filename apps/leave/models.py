from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Fully Approved'),
        ('Rejected', 'Rejected'),
    ]

    STAGE_CHOICES =[
        ('Trainer_Review', 'Awaiting Trainer/Staff Review'),
        ('Reporting_Review', 'Awaiting Reporting Person Review'),
        ('HR_Review','Awaiting HR Review'),
        ('Founder_Review', 'Awaiting Founder Review'),
    ]  

    APPLICANT_CHOICES =[
        ('Staff', 'Staff'),
        ('Student', 'Student')
    ]

    LEAVE_TYPE_CHOICES = [
        ('Sick Leave', 'Sick leave'),
        ('Casual Leave', 'Casual Leave '),
        ('Emergency Leave', 'Emergency Leave '),
        ('Exam Leave', 'Exam Leave '),
        ('Other', 'Other / Custom'),
    ]

    leave_id = models.AutoField(primary_key=True)    

    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    applicant_type = models.CharField(max_length=50, choices=APPLICANT_CHOICES)
    department = models.CharField(max_length=100, blank=True, null=True, default="Computer Science")

    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPE_CHOICES)
    from_date = models.DateField()
    to_date = models.DateField()
    days = models.IntegerField()
    reason = models.TextField(max_length=300)
    doc_path = models.FileField(upload_to='leave_documents/', blank=True, null=True)

    reporting_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_reviews')
    current_stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    
    reviewer_comments = models.TextField(blank=True, null=True)
    submission_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Leave {self.leave_id} - {self.applicant.username} ({self.applicant_type})"

class LeaveApproval(models.Model):
    approval_id = models.AutoField(primary_key=True)
    leave = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='approvals')
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_approvals')
    approver_role = models.CharField(max_length=50) 
    decision = models.CharField(max_length=15, choices=[('Approved', 'Approved'), ('Rejected', 'Rejected')])
    comment = models.TextField(max_length=300, blank=True, null=True)
    decided_at = models.DateTimeField(auto_now=True)

class LeaveBalance(models.Model):
    balance_id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_balances')
    year = models.IntegerField(default=2026)
    
    sick_total = models.IntegerField(default=12)
    sick_used = models.IntegerField(default=0)
    casual_total = models.IntegerField(default=10)
    casual_used = models.IntegerField(default=0)
    emergency_total = models.IntegerField(default=3)
    emergency_used = models.IntegerField(default=0)
    exam_total = models.IntegerField(default=5)
    exam_used = models.IntegerField(default=0)
    other_total = models.IntegerField(default=0)
    other_used = models.IntegerField(default=0)
    
    @property
    def dynamic_total_allocated(self):
        return self.sick_total + self.casual_total + self.emergency_total + self.exam_total + self.other_total
    
    @property
    def dynamic_total_used(self):
        return self.sick_used + self.casual_used + self.emergency_used + self.exam_used + self.other_used
    
    @property
    def dynamic_remaining_balance(self):
        return self.dynamic_total_allocated - self.dynamic_total_used
    
# class HolidayCalendar(models.Model):
#     HOLIDAY_TYPES = [
#         ('Government', 'Government Holiday'),
#         ('Semester', 'Semester Holiday'),
#         ('Institution', 'Institution Closure'),
#         ('Exam_Break', 'Exam Preparation Break'),
#     ]

#     holiday_id = models.AutoField(primary_key=True)
#     title = models.CharField(max_length=150)  # e.g., "Diwali", "Summer Vacation"
#     holiday_type = models.CharField(max_length=30, choices=HOLIDAY_TYPES)
#     start_date = models.DateField()
#     end_date = models.DateField()
#     description = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.title} ({self.get_holiday_type_display()})"    