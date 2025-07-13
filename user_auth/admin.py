from django.contrib import admin

# Register your models here.
from .models import EmailOTP
admin.site.register(EmailOTP)