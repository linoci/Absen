import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, time
from .models import User, Attendance, LeaveRequest
from .forms import AttendanceForm, LeaveRequestForm, ProfileUpdateForm, CustomPasswordChangeForm, AddEmployeeForm
from django.contrib.auth import update_session_auth_hash
from geopy.distance import geodesic
import base64
from django.core.files.base import ContentFile
import logging
import csv
from django.db.models import Q
from django.http import HttpResponse
from geopy.geocoders import Nominatim

# Koordinat Lokasi Kantor Kecamatan dan Kantor Kelurahan
KANTOR_KECAMATAN_COORDS = (-6.5933, 106.8211)  # Latitude, Longitude Kantor Kecamatan Cibinong
KANTOR_KELURAHAN_COORDS = (-6.472672084603338, 106.85352305180264)  # Latitude, Longitude Kantor Kelurahan Cibinong
MAX_DISTANCE = 1.0  # 1 kilometer

# Batas waktu jam kerja
CHECK_IN_LIMIT = time(7, 30)
CHECK_OUT_LIMIT = {
    'Mon-Thu': time(16, 0),
    'Fri': time(16, 30),
}

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        job_title = request.POST.get('job_title')

        # Autentikasi pengguna
        user = authenticate(request, username=username, password=password)

        if user:
            if user.job_title == job_title:
                login(request, user)
                # Arahkan berdasarkan job_title
                if job_title == 'Admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('staff_dashboard')
            else:
                messages.error(request, "Job title tidak sesuai dengan pengguna.")
        else:
            messages.error(request, "Username atau password salah.")

    return render(request, 'login.html')
@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html', {
        'greeting': "Selamat Datang, Admin!",  # Menampilkan "Selamat Datang"
        'username': request.user.username,    # Menampilkan nama pengguna (username)
    })

@login_required
def staff_dashboard(request):
    user = request.user
    today = datetime.now().date()

    # Periksa absensi hari ini
    absen_masuk = Attendance.objects.filter(user=user, timestamp__date=today, status='masuk').exists()
    absen_pulang = Attendance.objects.filter(user=user, timestamp__date=today, status='pulang').exists()

    # Hitung statistik kehadiran
    hadir_count = Attendance.objects.filter(user=user, status__in=['masuk', 'terlambat']).count()
    izin_count = Attendance.objects.filter(user=user, status='izin').count()
    sakit_count = Attendance.objects.filter(user=user, status='sakit').count()
    terlambat_count = Attendance.objects.filter(user=user, status='terlambat').count()

    return render(request, 'staff_dashboard.html', {
        'greeting': "Selamat Datang!",
        'username': user.username,
        'absen_masuk': absen_masuk,
        'absen_pulang': absen_pulang,
        'hadir_count': hadir_count,
        'izin_count': izin_count,
        'sakit_count': sakit_count,
        'terlambat_count': terlambat_count,
    })


@login_required
def absen(request):
    return render(request, 'absen.html')

@login_required
def cuti(request):
    return render(request, 'cuti.html')

@login_required
def history(request):
    return render(request, 'history.html')

@login_required
def attendance_view(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST, request.FILES)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.user = request.user
            attendance.save()
            messages.success(request, 'Absensi berhasil disimpan!')
        else:
            messages.error(request, 'Terjadi kesalahan saat menyimpan absensi.')
    else:
        form = AttendanceForm()
    return render(request, 'absen.html', {'form': form})

@login_required
def leave_request_view(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            leave_request.save()
            messages.success(request, 'Pengajuan cuti Anda berhasil diproses.')
        else:
            messages.error(request, 'Ada kesalahan dalam pengajuan Anda.')
    else:
        form = LeaveRequestForm()

    return render(request, 'cuti.html', {'form': form})

@login_required
def leave_status_view(request):
    leave_requests = LeaveRequest.objects.filter(user=request.user).order_by('-start_date')
    return render(request, 'status_cuti.html', {'leave_requests': leave_requests})

@login_required
def profile_view(request):
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profil berhasil diperbarui!")
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)
            messages.success(request, "Password berhasil diperbarui!")
    else:
        profile_form = ProfileUpdateForm(instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user)

    # Cek role pengguna untuk mengarahkan kembali ke dashboard yang sesuai
    if request.user.role == 'admin':
        dashboard_url = 'admin_dashboard'
    else:
        dashboard_url = 'staff_dashboard'

    return render(request, 'profile.html', {
        'profile_form': profile_form, 
        'password_form': password_form, 
        'dashboard_url': dashboard_url  # Kirim URL dashboard ke template
    })
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def take_attendance(request):
    if request.method == 'POST':
        current_time = datetime.now().time()
        day_of_week = datetime.now().strftime('%a')
        user = request.user

        # Ambil data lokasi dari request
        try:
            latitude = float(request.POST.get('latitude'))
            longitude = float(request.POST.get('longitude'))
        except (TypeError, ValueError):
            messages.error(request, 'Lokasi tidak valid. Pastikan GPS aktif.')
            return redirect('attendance_view')

        # Proses foto dari base64
        photo_data = request.POST.get('photo')
        if photo_data:
            try:
                photo_data = photo_data.split(',')[1]
                photo_file = ContentFile(base64.b64decode(photo_data), name='attendance.jpg')
            except (IndexError, TypeError, base64.binascii.Error):
                messages.error(request, 'Gagal memproses foto.')
                return redirect('attendance_view')
        else:
            messages.error(request, 'Foto tidak ditemukan.')
            return redirect('attendance_view')

        # Cek apakah absensi sudah dilakukan
        attendance_today = Attendance.objects.filter(
            user=user, timestamp__date=datetime.now().date()
        )

        # Hitung jarak dari lokasi pegawai ke kedua kantor
        pegawai_coords = (latitude, longitude)
        distance_to_kantor_kecamatan = geodesic(pegawai_coords, KANTOR_KECAMATAN_COORDS).kilometers
        distance_to_kantor_kelurahan = geodesic(pegawai_coords, KANTOR_KELURAHAN_COORDS).kilometers

        if distance_to_kantor_kecamatan <= MAX_DISTANCE or distance_to_kantor_kelurahan <= MAX_DISTANCE:
            # Lokasi valid (berada di salah satu kantor)
            if not attendance_today.filter(status='masuk').exists():
                # Absensi masuk
                status = 'masuk' if current_time <= CHECK_IN_LIMIT else 'terlambat'
                Attendance.objects.create(
                    user=user,
                    latitude=latitude,
                    longitude=longitude,
                    photo=photo_file,
                    status=status
                )
                messages.success(request, f"Absensi {status} berhasil dicatat.")
            elif not attendance_today.filter(status='pulang').exists():
                # Absensi pulang
                expected_time = CHECK_OUT_LIMIT['Mon-Thu'] if day_of_week in ['Mon', 'Tue', 'Wed', 'Thu'] else CHECK_OUT_LIMIT['Fri']
                if current_time >= expected_time:
                    Attendance.objects.create(
                        user=user,
                        latitude=latitude,
                        longitude=longitude,
                        photo=photo_file,
                        status='pulang'
                    )
                    messages.success(request, "Absensi pulang berhasil dicatat.")
                else:
                    messages.error(request, "Belum waktunya untuk absen pulang.")
            else:
                messages.warning(request, "Anda sudah melakukan absensi masuk dan pulang hari ini.")
        else:
            messages.error(request, "Anda tidak berada dalam jangkauan kantor Kecamatan atau Kelurahan.")

        return redirect('attendance_view')

    return render(request, 'attendance.html')

@login_required
def attendance_report(request):
    today = datetime.now().date()
    attendance_today = Attendance.objects.filter(
        timestamp__date=today
    ).order_by('timestamp')
    return render(request, 'report.html', {'attendance_today': attendance_today})

@login_required
def history(request):
    user = request.user
    # Retrieve all attendance records for the logged-in user
    attendance_records = Attendance.objects.filter(user=user).order_by('-timestamp')

    return render(request, 'history.html', {'attendance_records': attendance_records})

@login_required
def data_absen(request):
    # Get filter parameters
    name = request.GET.get('name', '')
    month = request.GET.get('month', '')
    year = request.GET.get('year', '')

    # Filter records
    attendance_records = Attendance.objects.all()
    if name:
        attendance_records = attendance_records.filter(user__username__icontains=name)
    if month:
        attendance_records = attendance_records.filter(timestamp__month=month)
    if year:
        attendance_records = attendance_records.filter(timestamp__year=year)

    # Pass range of months and years
    context = {
        'attendance_records': attendance_records,
        'name': name,
        'month': month,
        'year': year,
        'months': range(1, 13),
        'years': range(2020, datetime.now().year + 1),
    }
    return render(request, 'data_absen.html', context)


@login_required
def export_to_excel(request):
    # Get filter parameters
    name = request.GET.get('name', '')
    month = request.GET.get('month', '')
    year = request.GET.get('year', '')

    # Filter records
    attendance_records = Attendance.objects.all()
    if name:
        attendance_records = attendance_records.filter(user__username__icontains=name)
    if month:
        attendance_records = attendance_records.filter(timestamp__month=month)
    if year:
        attendance_records = attendance_records.filter(timestamp__year=year)

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Username', 'Status', 'Date', 'Time', 'Latitude', 'Longitude'])

    for record in attendance_records:
        writer.writerow([
            record.user.username,
            record.status,
            record.timestamp.strftime('%Y-%m-%d'),
            record.timestamp.strftime('%H:%M'),
            record.latitude or 'N/A',
            record.longitude or 'N/A',
        ])

    return response

@login_required
def leave_requests_list(request):
    # Ensure only admin can access this view
    if request.user.role != 'admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('staff_dashboard')

    # Get all leave requests
    leave_requests = LeaveRequest.objects.all().order_by('-created_at')
    return render(request, 'leave_requests_list.html', {'leave_requests': leave_requests})


@login_required
def update_leave_status(request, leave_id):
    # Ensure only admin can update statuses
    if request.user.role != 'admin':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('staff_dashboard')

    # Get leave request
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['Approved', 'Rejected', 'Pending']:
            leave_request.status = new_status
            leave_request.save()
            messages.success(request, f"Leave request status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status selected.")

    return redirect('leave_requests_list')

@login_required
def add_employee(request):
    # Restrict access to admins only
    if request.user.role != 'admin':
        messages.error(request, "You do not have permission to add employees.")
        return redirect('staff_dashboard')

    if request.method == 'POST':
        form = AddEmployeeForm(request.POST)
        if form.is_valid():
            # Save the user instance
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()
            messages.success(request, "Employee added successfully!")
            return redirect('employee_list')  # Updated to valid URL
        else:
            messages.error(request, "Error adding employee. Please check the form.")
    else:
        form = AddEmployeeForm()

    return render(request, 'add_employee.html', {'form': form})

@login_required
def employee_list(request):
    # Ensure only admin can access this view
    if request.user.role != 'admin':
        messages.error(request, "You do not have permission to view this page.")
        return redirect('staff_dashboard')

    # Retrieve all users except superusers
    employees = User.objects.filter(is_superuser=False).order_by('username')
    return render(request, 'employee_list.html', {'employees': employees})

@login_required
def delete_employee(request, employee_id):
    # Ensure only admin can delete employees
    if request.user.role != 'admin':
        messages.error(request, "You do not have permission to delete employees.")
        return redirect('staff_dashboard')

    # Get the employee to delete
    employee = get_object_or_404(User, id=employee_id)
    
    # Delete the employee
    employee.delete()
    messages.success(request, "Employee deleted successfully!")
    
    return redirect('employee_list')

def job_title_view(request):
    # Dapatkan semua user beserta role dan job_title mereka
    users = User.objects.all().order_by('role', 'job_title')  # Urutkan berdasarkan role dan job_title
    context = {
        'users': users,
    }
    return render(request, 'job_title_list.html', context)

