from django.urls import path
from .views import *
from user_auth.views import AcceptRequest, RejectRequest,ListOfStudents,AcceptRequestUser, GetMentorRequest, GetMenteeRequest
from users.views import FreeTimeSlotView, GmeetScheduleView

urlpatterns = [
    path('requests/mentor/',GetMentorRequest.as_view(),name="Mentor-Request"),
    path('requests/mentee/',GetMenteeRequest.as_view(),name="Mentee-Request"),
    path('requests/<int:booking_id>/',AcceptRequest.as_view(),name="accept-Request"),
    path('requests/user/<int:user_id>/',AcceptRequestUser.as_view(),name="accept-Request-user-id"),
    path('requests/reject/<int:booking_id>/',RejectRequest.as_view(),name="accept-Request"),
    path('list/',ListOfStudents.as_view(),name="list-students"),
    path('freetime/', FreeTimeSlotView.as_view(), name='freetime'),
    path('schedule-meeting/', GmeetScheduleView.as_view(), name='schedule-meeting'),

    path('users/', UserListView.as_view(), name='user-list'),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('profile/edit/', ProfileUpdate.as_view(), name='profile-update'),
    path('mentors/', MentorList.as_view(), name='list-mentors'),
    path('metrics/', Metrics.as_view(), name='metrics'),
    path('mentee/', Fieldofinterest.as_view(), name='become-a-mentee'),
    path('mentor/', ExpertField.as_view(), name='update-expertise'),
    path('booking/', BookingCreateView.as_view(), name='create-booking'),
    path('interests/', InterestListView.as_view(), name='list-interests'),
]