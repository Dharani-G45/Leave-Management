from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('reporting-dashboard/', views.reporting_dashboard, name='reporting_dashboard'),
    path('hr-dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('founder-dashboard/', views.founder_dashboard, name='founder_dashboard'),

    path('apply/', views.apply_leave, name='apply_leave'),
    path('approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('reject/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    path('api/leave-events/', views.get_leave_events, name='leave-events'),

    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
]