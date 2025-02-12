# Generated by Django 5.1.3 on 2024-11-30 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='is_valid',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='type',
            field=models.CharField(default='masuk', max_length=10),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='attendance_photos/'),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='status',
            field=models.CharField(choices=[('masuk', 'Masuk'), ('pulang', 'Pulang'), ('izin', 'Izin'), ('sakit', 'Sakit'), ('tidak hadir', 'Tidak Hadir'), ('terlambat', 'Terlambat')], max_length=20),
        ),
    ]
