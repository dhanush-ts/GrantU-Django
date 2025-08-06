from django.urls import path
from .views import *

urlpatterns = [    
    path('requests/mentor/',GetMentorRequest.as_view(),name="Mentor-Request"),
    path('requests/mentee/',GetMenteeRequest.as_view(),name="Mentee-Request"),
    path('requests/<int:Connection_id>/',AcceptRequest.as_view(),name="accept-Request"),
    path('requests/user/<int:user_id>/',AcceptRequestUser.as_view(),name="accept-Request-user-id"),
    path('requests/reject/<int:Connection_id>/',RejectRequest.as_view(),name="accept-Request"),
    
    path('list/',ListOfStudents.as_view(),name="list-students"),
    
    path('freetime/', FreeTimeSlotView.as_view(), name='freetime'),
    
    path('schedule-meeting/', GmeetScheduleView.as_view(), name='schedule-meeting'),
    path('connection/', ConnectionCreateView.as_view(), name='create-connection'),
]