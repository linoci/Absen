# Generated by Django 5.1.3 on 2024-11-30 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_attendance_is_valid_attendance_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='job_title',
            field=models.CharField(blank=True, choices=[('Tenaga Administrasi', 'Tenaga Administrasi'), ('Petugas Kebersihan', 'Petugas Kebersihan'), ('Petugas Keamanan', 'Petugas Keamanan'), ('Admin', 'Admin')], max_length=30, null=True),
        ),
    ]
