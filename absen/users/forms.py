from django import forms
from .models import Attendance
from .models import LeaveRequest
from django.contrib.auth.forms import PasswordChangeForm
from .models import User

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['photo', 'latitude', 'longitude', 'status']
        widgets = {
            'status': forms.HiddenInput(),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

from django import forms
from .models import User

class AddEmployeeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), label='Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}), label='Confirm Password')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'role', 'job_title', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Nama Depan'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nama Belakang'}),
            'username': forms.TextInput(attrs={'placeholder': 'NamaUser'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'role': forms.Select(attrs={'placeholder': 'Role'}),
            'job_title': forms.Select(attrs={'placeholder': 'Nama Jabatan'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
