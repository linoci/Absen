from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('attendance/', views.attendance_view, name='attendance_view'),
    path('absen/', views.attendance_view, name='attendance'),
    path('history/', views.history, name='history'),
    path('cuti/', views.leave_request_view, name='leave_request'),
    path('status-cuti/', views.leave_status_view, name='leave_status'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.user_logout, name='logout'),
    path('take-attendance/', views.take_attendance, name='take_attendance'),
    path('report/', views.attendance_report, name='attendance_report'),
    path('profile_adm/', views.profile_view, name='profile_adm'),
    path('data-absen/', views.data_absen, name='data_absen'),
    path('export-to-excel/', views.export_to_excel, name='export_to_excel'),
    path('leave-requests/', views.leave_requests_list, name='leave_requests_list'),
    path('update-leave-status/<int:leave_id>/', views.update_leave_status, name='update_leave_status'),
    path('add-employee/', views.add_employee, name='add_employee'),
    path('employee-list/', views.employee_list, name='employee_list'),
    path('delete-employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    path('job_title_view/', views.job_title_view, name='job_title_view'),

]
