from django.urls import path
from .views import *
from connections.views import *

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('profile/edit/', ProfileUpdate.as_view(), name='profile-update'),
    path('mentors/', MentorList.as_view(), name='list-mentors'),
    path('metrics/', Metrics.as_view(), name='metrics'),
    path('mentee/', Fieldofinterest.as_view(), name='become-a-mentee'),
    path('mentor/', ExpertField.as_view(), name='update-expertise'),
    path('interests/', InterestListView.as_view(), name='list-interests'),
]