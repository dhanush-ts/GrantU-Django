# Generated by Django 5.1.4 on 2025-07-20 12:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_gmeetschedule'),
    ]

    operations = [
        migrations.CreateModel(
            name='FreeTimeSlots',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Day', models.CharField(max_length=20)),
                ('Start_Time', models.TimeField()),
                ('End_Time', models.TimeField()),
                ('Created_At', models.DateTimeField(auto_now_add=True)),
                ('User', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.userdetails')),
            ],
        ),
    ]
