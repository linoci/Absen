from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Attendance, LeaveRequest

class CustomUserAdmin(UserAdmin):
    # Fields yang akan ditampilkan di daftar pengguna
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'job_title', 'is_staff', 'is_active')
    
    # Tambahkan filter untuk mempermudah pencarian
    list_filter = ('role', 'job_title', 'is_staff', 'is_active')
    
    # Tambahkan field ini untuk digunakan di form detail user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Roles & Job', {'fields': ('role', 'job_title')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Fields untuk form pendaftaran pengguna baru
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'job_title', 'is_staff', 'is_active'),
        }),
    )
    
    # Tambahkan kolom pencarian
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

# Daftarkan model User dengan CustomUserAdmin
admin.site.register(User, CustomUserAdmin)

# Custom admin untuk model Attendance
class AttendanceAdmin(admin.ModelAdmin):
    # Kolom yang akan ditampilkan di daftar absensi
    list_display = ('user', 'timestamp', 'status', 'latitude', 'longitude', 'photo')
    
    # Filter berdasarkan status dan user
    list_filter = ('status', 'user')
    
    # Kolom pencarian untuk nama user
    search_fields = ('user__username', 'user__email')
    
    # Urutan default
    ordering = ('-timestamp',)

# Daftarkan model Attendance dengan AttendanceAdmin
admin.site.register(Attendance, AttendanceAdmin)

class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'status', 'created_at')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('user__username', 'reason')
    ordering = ('-created_at',)

admin.site.register(LeaveRequest, LeaveRequestAdmin)

