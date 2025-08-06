from django.contrib import admin

# Register your models here.
from .models import UserDetails,Educational_levels, Interest
from connections.models import Connection, GmeetSchedule, FreeTimeSlots

# Register your models here.
admin.site.register(UserDetails)
admin.site.register(Educational_levels)
admin.site.register(Connection)
admin.site.register(Interest)
admin.site.register(GmeetSchedule)
admin.site.register(FreeTimeSlots)