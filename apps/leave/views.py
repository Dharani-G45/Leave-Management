import random
import os
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.models import User
from profiles.models import Profile
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from .models import LeaveRequest, LeaveApproval, LeaveBalance 

print(f"DEBUG: EMAIL_HOST_PASSWORD is: {os.environ.get('EMAIL_HOST_PASSWORD')}")
# --- HELPER FUNCTIONS ---
def get_balances(user):
    balance_record = LeaveBalance.objects.filter(staff_id=user).first()
    
    # 1. Get the "Total" from your model (or defaults)
    s_t = balance_record.sick_total if balance_record else 12
    c_t = balance_record.casual_total if balance_record else 10
    e_t = balance_record.emergency_total if balance_record else 3
    x_t = balance_record.exam_total if balance_record else 5
    o_t = balance_record.other_total if balance_record else 0

    def get_used(l_type):
        return LeaveRequest.objects.filter(
            applicant=user, 
            leave_type=l_type, 
            status='Approved'
        ).aggregate(Sum('days'))['days__sum'] or 0

    s_u = get_used('Sick Leave')
    c_u = get_used('Casual Leave')
    e_u = get_used('Emergency Leave')
    x_u = get_used('Exam Leave')
    o_u = get_used('Other Leave')

    total_allocated = s_t + c_t + e_t + x_t + o_t
    total_used = s_u + c_u + e_u + x_u + o_u
    
    return {
        'sick_total': s_t, 'sick_used': s_u, 'sick_remaining': s_t - s_u,
        'casual_total': c_t, 'casual_used': c_u, 'casual_remaining': c_t - c_u,
        'emergency_total': e_t, 'emergency_used': e_u, 'emergency_remaining': e_t - e_u,
        'exam_total': x_t, 'exam_used': x_u, 'exam_remaining': x_t - x_u,
        'other_total': o_t, 'other_used': o_u, 'other_remaining': o_t - o_u,
        'total_allocated': total_allocated,
        'total_used': total_used,
        'total_remaining': total_allocated - total_used
    }

def get_dashboard_url(user):
    role = user.profile.role.lower().replace(' ', '_')
    role_map = {
        'student': 'dashboard',
        'staff': 'staff_dashboard',
        'reporting_person': 'reporting_dashboard',
        'hr': 'hr_dashboard',
        'founder': 'founder_dashboard',
    }
    return role_map.get(role, 'dashboard')

def send_leave_email(recipient_email, subject, leave_request):
    body = (
        f"Hello,\n\n"
        f"Update on Leave Request (ID: {leave_request.leave_id}):\n"
        f"Applicant: {leave_request.applicant.get_full_name()}\n"
        f"Status: {leave_request.status}\n"
        f"Current Stage: {leave_request.current_stage}\n\n"
        f"Please log in to your dashboard to review."
    )
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient_email], fail_silently=False)
    
def get_user_remaining_days(user, leave_type):
    total_allocated = getattr(user.profile, f"{leave_type.lower().replace(' ', '_')}_total", 0)
     
    used_days = LeaveRequest.objects.filter(
        applicant=user, 
        leave_type=leave_type, 
        status='Approved'
    ).aggregate(total=Sum('days'))['total'] or 0
    
    return total_allocated - used_days

def deduct_leave_balance(leave):
    balance = LeaveBalance.objects.filter(staff_id=leave.applicant).first()
    if not balance: return
    mapping = {
        'Sick Leave': 'sick_used', 'Casual Leave': 'casual_used',
        'Emergency Leave': 'emergency_used', 'Exam Leave': 'exam_used',
        'Other Leave': 'other_used'
    }
    field_name = mapping.get(leave.leave_type)
    if field_name and hasattr(balance, field_name):
        current_used = getattr(balance, field_name)
        setattr(balance, field_name, current_used + int(leave.days))
        balance.save()

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user:
                auth_login(request, user)
                role = user.profile.role.lower().strip().replace(' ', '_') 
                
                mapping = {
                    'hr': 'hr_dashboard',
                    'founder': 'founder_dashboard',
                    'staff': 'staff_dashboard',
                    'reporting_person': 'reporting_dashboard', # Note the underscore
                    'student': 'dashboard'
                }
                
                return redirect(mapping.get(role, 'dashboard'))
        messages.error(request, "Invalid credentials.")
    return render(request, 'leave/login.html', {'form': AuthenticationForm()})

def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        role = request.POST.get('role', 'STUDENT')
        email = request.POST.get('email')
        reporting_person_id = request.POST.get('reporting_person') 
        
        user = User.objects.create_user(
            username=username, 
            password=request.POST.get('password'), 
            email=email,
            first_name=request.POST.get('first_name'), 
            last_name=request.POST.get('last_name')
        )
        reporting_profile = None
        if reporting_person_id:
            reporting_profile = Profile.objects.get(id=reporting_person_id)

        Profile.objects.create(
            user=user, 
            role=role, 
            id_number=f"CSC-{role}-{random.randint(1000,9999)}", 
            email=email,
            branch_department=request.POST.get('branch_department'),
            reporting_person=reporting_profile
        )
        messages.success(request, "Account created successfully.")
        return redirect('login_user')
    
    managers = Profile.objects.filter(role__in=['STAFF', 'HR', 'FOUNDER', 'Reporting Person', 'REPORTING PERSON'])
    return render(request, 'leave/register.html', {'managers': managers})


def get_leave_events(request):
    leaves = LeaveRequest.objects.filter(status='Approved')
    events = []
    for leave in leaves:
        events.append({
            'title': f"{leave.applicant.username} - {leave.leave_type}",
            'start': leave.from_date.isoformat(),
            'end': leave.to_date.isoformat(),
            'className': 'bg-primary'
        })
    return JsonResponse(events, safe=False)

@login_required
def dashboard(request):
    return render(request, 'leave/dashboard.html', {
        'balances': get_balances(request.user),
        'my_requests': LeaveRequest.objects.filter(applicant=request.user).order_by('-leave_id')
    })

@login_required
def staff_dashboard(request):
    pending_tasks = LeaveRequest.objects.filter(
        reporting_person=request.user,
        status='Pending',
        current_stage__in=['Trainer_Review', 'Reporting_Review'] 
    ).order_by('-leave_id')

    return render(request, 'leave/staff_dashboard.html', {
        'balances': get_balances(request.user),
        'my_requests': LeaveRequest.objects.filter(applicant=request.user).order_by('-leave_id'),
        'pending_requests': pending_tasks,
        'processed_history': LeaveApproval.objects.filter(approver=request.user).order_by('-approval_id')
    })

@login_required
def reporting_dashboard(request):
    pending_tasks = LeaveRequest.objects.filter(
        reporting_person=request.user,
        status='Pending',
        current_stage__in=[ 'Reporting_Review'] 
    ).order_by('-leave_id')
    
    print(f"DEBUG: User is {request.user.username}")
    print(f"DEBUG: User role is {request.user.profile.role}")
    return render(request, 'leave/reporting_dashboard.html', {
        'balances': get_balances(request.user),
        'my_requests': LeaveRequest.objects.filter(applicant=request.user).order_by('-leave_id'),
        'pending_requests': pending_tasks,
        'processed_history': LeaveApproval.objects.filter(approver=request.user).order_by('-approval_id')
    })

@login_required
def hr_dashboard(request):
    if request.user.profile.role.lower() != 'hr':
        return redirect('dashboard')
    
    events = []
    
    # for h in HolidayCalendar.objects.filter(end_date__gte=timezone.now().date()):
    #     events.append({
    #         'title': h.title,
    #         'start': h.start_date.strftime('%Y-%m-%d'),
    #         'end': (h.end_date + timezone.timedelta(days=1)).strftime('%Y-%m-%d'),
    #         'backgroundColor': '#e74c3c' if h.holiday_type == 'Government' else '#2ecc71',
    #         'allDay': True,
    #         'type': h.get_holiday_type_display()
    #     })
    for l in LeaveRequest.objects.filter(status='Approved'):
        events.append({
            'title': l.applicant.username,
            'start': l.from_date.strftime('%Y-%m-%d'),
            'end': (l.to_date + timezone.timedelta(days=1)).strftime('%Y-%m-%d'),
            'backgroundColor': '#3498db',
            'allDay': True,
            'type': 'Employee Leave'
        })
    
    context = {
        #'calendar_events_json': json.dumps(events),
        'my_requests': LeaveRequest.objects.filter(applicant=request.user),
        'pending_requests': LeaveRequest.objects.filter(status='Pending'),
        'processed_history': LeaveApproval.objects.all().order_by('-approval_id'),
    }
    return render(request, 'leave/hr_dashboard.html', context)

@login_required
def founder_dashboard(request):
    if request.user.profile.role.lower() != 'founder':
        return redirect('dashboard')
    
    pending = LeaveRequest.objects.filter(status='Pending', current_stage='Founder_Review')
    history = LeaveApproval.objects.all().order_by('-decided_at')
    
    context = {
        'pending_requests': pending,
        'approval_history': history,
        'rejected_requests': LeaveRequest.objects.filter(status='Rejected'),
    }
    return render(request, 'leave/founder_dashboard.html', context)

# --- LEAVE ACTIONS ---
@login_required
def apply_leave(request):
    if request.method == 'POST':
        user = request.user
        leave_type = request.POST.get('leave_type')
        requested_days = int(request.POST.get('days', 0))

        # 1. BALANCE CHECK LOGIC
        # Assuming you have a way to calculate remaining days (e.g., from your profile or a helper)
        # Replace 'get_user_remaining_days' with your specific model logic
        remaining_days = get_user_remaining_days(user, leave_type) 

        if requested_days > remaining_days:
            return JsonResponse({
                'status': 'error', 
                'message': f'Insufficient balance! You requested {requested_days} days, but only {remaining_days} are available.'
            }, status=400)
        role = user.profile.role.lower().replace(' ', '_')
        
        if role == 'student':
            reviewer = user.profile.reporting_person.user if user.profile.reporting_person else None
            stage = 'Trainer_Review'
            
        elif role == 'staff':
            reviewer = user.profile.reporting_person.user if user.profile.reporting_person else None
            stage = 'Reporting_Review'
            
        elif role == 'reporting_person':
            reviewer = User.objects.filter(profile__role__iexact='HR').first()
            stage = 'HR_Review'
            
        elif role == 'hr':
            reviewer = User.objects.filter(profile__role__iexact='Founder').first()
            stage = 'Founder_Review'
        else:
            reviewer = None
            stage = 'Founder_Review'

        if not reviewer:
            reviewer = User.objects.filter(profile__role__iexact='HR').first()
            stage = 'HR_Review'
 

        leave = LeaveRequest.objects.create(
            applicant=user, 
            leave_type=request.POST.get('leave_type'),
            from_date=request.POST.get('from_date'),
            to_date=request.POST.get('to_date'),
            reason=request.POST.get('reason'),
            days=request.POST.get('days'),
            reporting_person=reviewer,
            current_stage=stage,
            status='Pending'
        )
        if reviewer and reviewer.email:
            send_leave_email(reviewer.email, "New Leave Request Pending", leave)
        else:
            print(f"No reviewer found for role {role}. Leave ID: {leave.leave_id}")
            
       
        dashboard_map = {
            'student': 'dashboard',
            'staff': 'staff_dashboard',
            'reporting_person': 'reporting_dashboard',
            'hr': 'hr_dashboard',
            'founder': 'founder_dashboard'
        }
        role = request.user.profile.role.lower().replace(' ', '_')
        return JsonResponse({'status': 'success', 'message': 'Request submitted successfully!'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def approve_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, leave_id=leave_id)
    role = leave.applicant.profile.role.lower().replace(' ', '_')
    

    paths = {
        'student': ['Trainer_Review'], 
        'staff': ['Reporting_Review', 'HR_Review', 'Founder_Review'],
        'reporting_person': ['HR_Review', 'Founder_Review'],
        'hr': ['Founder_Review']
    }
    
    path = paths.get(role, [])
    try:
        current_index = path.index(leave.current_stage)
    except ValueError:
        current_index = -1

    if current_index == len(path) - 1:
        leave.status = 'Approved'
        deduct_leave_balance(leave)
    else:
        next_stage = path[current_index + 1]
        leave.current_stage = next_stage
        
        if next_stage == 'Reporting_Review':
            leave.reporting_person = leave.applicant.profile.reporting_person.user
        elif next_stage == 'HR_Review':
            leave.reporting_person = User.objects.filter(profile__role__iexact='HR').first()
        elif next_stage == 'Founder_Review':
            leave.reporting_person = User.objects.filter(profile__role__iexact='Founder').first()
        
    leave.save()

    try:
        send_leave_email(leave.applicant.email, "Leave Approved", leave)
        print("DEBUG: Approval email sent successfully")
    except Exception as e:
        print(f"DEBUG: Email sending FAILED: {e}")

              
    LeaveApproval.objects.create(
        leave=leave, 
        approver=request.user, 
        decision='Approved', 
        comment="Approved"
    )
    return JsonResponse({'status': 'success', 'message': 'Approved'})

@login_required
def reject_leave(request, leave_id):
    if request.method != 'POST':
        return redirect('dashboard') 
        
    leave = get_object_or_404(LeaveRequest, leave_id=leave_id)
    comment = request.POST.get('reviewer_comments')
    
    if not comment:
        messages.error(request, "Rejection reason required.")
        return redirect('dashboard')
    
    leave.status = 'Rejected'
    leave.current_stage = 'Completed' 
    leave.save()
    
    # Create Log
    LeaveApproval.objects.create(
        leave=leave, 
        approver=request.user, 
        decision='Rejected', 
        comment=comment
    )
    
    send_leave_email(leave.applicant.email, "Leave Rejected", leave)
    
    return JsonResponse({'status': 'success', 'message': 'Rejected'})
