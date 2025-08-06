from django.db import models
from users.models import UserDetails, Interest
from django.utils import timezone

# Create your models here.
class Connection(models.Model):
    Connection_ID = models.AutoField(primary_key=True)
    Mentor = models.ForeignKey(
        UserDetails, 
        to_field='User_ID',
        on_delete=models.CASCADE,
        related_name='mentor_connections'
    )
    Mentee = models.ForeignKey(
        UserDetails, 
        to_field='User_ID',
        on_delete=models.CASCADE,
        related_name='mentee_connections'
    )
    Description = models.TextField(blank=True, null=True)
    Details = models.TextField(blank=True, null=True)

    SELECTION_CHOICES = [
        ('mentor', 'Mentor chose mentee'),
        ('mentee', 'Mentee chose mentor'),
        ('system', 'System assigned'),
    ]

    Selection_By = models.CharField(
        max_length=10,
        choices=SELECTION_CHOICES,
        default='system'
    )
    status = models.CharField(max_length=10,choices=[
        ('pending', 'Not Accepted Yet'),
        ('accepted', 'Confirmed'),
        ('rejected', 'Rejected')
    ],default='pending')
    Interests = models.ManyToManyField(Interest, blank=True)   
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True) 

    def __str__(self):
        return f"Connection {self.Mentor.First_Name} - {self.Mentee.First_Name} - {self.status} - {self.Selection_By}"

class GmeetSchedule(models.Model):
    Connection = models.ForeignKey(Connection, to_field='Connection_ID', on_delete=models.CASCADE)
    Meeting_Link = models.URLField(max_length=200, blank=True, null=True)
    Meeting_Start_Time = models.DateTimeField(default=timezone.now)
    Meeting_End_Time = models.DateTimeField(null=True, blank=True)
    Description = models.TextField(blank=True, null=True)
    Created_At = models.DateTimeField(auto_now_add=True)
    Active = models.BooleanField(default=True)

    def __str__(self):
        return f"Gmeet for Connection {self.Connection.Connection_ID}"

class FreeTimeSlots(models.Model):
    User = models.ForeignKey(UserDetails, to_field='User_ID', on_delete=models.CASCADE)
    Day = models.CharField(max_length=20)
    Start_Time = models.TimeField()
    End_Time = models.TimeField()
    Created_At = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Free Slot for {self.User.First_Name} from {self.Start_Time} to {self.End_Time}"