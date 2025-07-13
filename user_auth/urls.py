from django.urls import path
from .views import *

urlpatterns = [
    path('register-request/', RegisterView.as_view(),name='user-create'),
    path('register-verify/', RegisterVerify.as_view(), name='email-verify'),
    path('login/', LoginView.as_view(), name='login'),




    path('forgot-password/', ForgotPasswordView.as_view(),name="forgot pass"),
    path('verify-reset-otp/', VerifyResetOTPView.as_view(),name="verify pass"),
    path('set-new-password/', SetNewPasswordView.as_view(),name="setting-new pass"),


 
]