from django.contrib import admin



# Register your models here.
from .models import Scholarship,User_Scholarship,Source

admin.site.register(Scholarship)
admin.site.register(User_Scholarship)
admin.site.register(Source)
