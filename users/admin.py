from django.contrib import admin

# Register your models here.
from .models import UserDetails,Educational_levels,Booking, Interest, GmeetSchedule, FreeTimeSlots

# Register your models here.
admin.site.register(UserDetails)
admin.site.register(Educational_levels)
admin.site.register(Booking)
admin.site.register(Interest)
admin.site.register(GmeetSchedule)
admin.site.register(FreeTimeSlots)