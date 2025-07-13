from django.db import models
from users.models import UserDetails
# Create your models here.
class Source(models.Model):
    Source_ID = models.AutoField(primary_key=True)
    Source_Name = models.CharField(max_length=255)
    Website_URL = models.URLField(max_length=255, blank=True, null=True)
    Scraper_Order = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.Source_Name
    
class Scholarship(models.Model):
    Scholarship_ID = models.AutoField(primary_key=True)
    Scholarship_Name = models.CharField(max_length=255)
    Scholarship_Description = models.TextField(blank=True, null=True)
    Scholarship_Amount = models.IntegerField(blank=True, null=True)
    Start_Date = models.DateTimeField(blank=True, null=True)
    Deadline = models.DateTimeField(blank=True, null=True)
    Eligibility_Criteria = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    Status = models.CharField(max_length=50, blank=True, null=True)
    Source_ID = models.ForeignKey(Source, to_field='Source_ID', on_delete=models.CASCADE, blank=True, null=True)
    Created_At = models.DateTimeField(auto_now_add=True)
    Updated_At = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.Scholarship_Name


class User_Scholarship(models.Model):
    User_ID = models.ForeignKey(UserDetails, to_field='User_ID', on_delete=models.CASCADE)
    Scholarship_ID = models.ForeignKey(Scholarship, to_field='Scholarship_ID', on_delete=models.CASCADE)
    Application_Status = models.CharField(max_length=50)
    Applied_Date = models.DateTimeField(auto_now_add=True)
    Review_Date = models.DateTimeField(blank=True, null=True)
    Rejection_Reason = models.TextField(blank=True, null=True)
    is_withdrawn = models.BooleanField(default=False)
    withdrawn_date = models.DateTimeField(blank=True, null=True)
    withdrawal_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('User_ID', 'Scholarship_ID')
        
    def __str__(self):
        return f"Application {self.id}"