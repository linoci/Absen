from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import time

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    job_title = models.CharField(
        max_length=30,
        choices=[
            ('Tenaga Administrasi', 'Tenaga Administrasi'),
            ('Petugas Kebersihan', 'Petugas Kebersihan'),
            ('Petugas Keamanan', 'Petugas Keamanan'),
            ('Admin', 'Admin'),
        ],
        blank=True,
        null=True,
    )
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('masuk', 'Masuk'),
        ('pulang', 'Pulang'),
        ('izin', 'Izin'),
        ('sakit', 'Sakit'),
        ('tidak hadir', 'Tidak Hadir'),
        ('terlambat', 'Terlambat'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='attendance_photos/', blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(default=now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    type = models.CharField(max_length=10, default='masuk')  # Additional field for attendance type
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp} - {self.status}"

class LeaveRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user.username} - {self.status}"

