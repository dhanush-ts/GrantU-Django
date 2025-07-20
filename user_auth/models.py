from django.db import models
from users.models import UserDetails

class EmailOTP(models.Model):
    email = models.OneToOneField(UserDetails,on_delete=models.CASCADE,related_name="email_otp")
    otp = models.CharField(max_length=6)
    

    def __str__(self):
        return str(self.email)
