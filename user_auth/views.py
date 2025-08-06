from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import EmailOTP
import random
from rest_framework import status
from users.serializer import *
from users.authentication import *
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from connections.serializers import *
from rest_framework.decorators import api_view
from .models import UserDetails
from django.shortcuts import redirect


@api_view(['GET'])
def finalize_google_login(request):
    social_user = request.user  # This is the user created by social-auth (we'll ignore saving it)
    print(social_user)

    if not social_user or not social_user.is_authenticated:
        return Response({"error": "User not authenticated"}, status=400)

    email = getattr(social_user, 'email', None)
    user, created = UserDetails.objects.get_or_create(
        Email_Address=email,
        defaults={
            'First_Name': social_user.first_name or "First",
            'Last_Name': social_user.last_name or "Last",
            'Phone_Number': "",  # default empty phone,
        }
    )

    # Now delete the Django default user (optional)
    social_user.delete()

    # Create your custom token
    token = generate_token(user)
    
    frontend_redirect_url = f"http://localhost:5173/?token={token}"

    return redirect(frontend_redirect_url)

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = f"{random.randint(0, 999999):06}"
            EmailOTP.objects.update_or_create(
                email=user,
                defaults={'otp': otp}
            )

            html_message = render_to_string('otp_email.html', {
                'otp': otp,
                'user_name': user.First_Name
            })
            plain_message = strip_tags(html_message)

            send_mail(
                subject="GrantU OTP Verification",
                message=plain_message,
                from_email="noreply@otp.com",
                recipient_list=[user.Email_Address],
                html_message=html_message,
            )

            token = generate_token(user)
            return Response({'token': token}, status=status.HTTP_201_CREATED)

        if "Email_Address" in serializer.errors:
            if "already exists" in str(serializer.errors["Email_Address"]):
                return Response({'error': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = UserDetails.objects.get(Email_Address=email)
        except UserDetails.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user and len(password)!=0 and password == user.Password and not user.is_verified:
            otp = f"{random.randint(0, 999999):06}"
            EmailOTP.objects.update_or_create(
                email=user,
                defaults={'otp': otp}
            )

            html_message = render_to_string('otp_email.html', {
                'otp': otp,
                'user_name': user.First_Name
            })
            plain_message = strip_tags(html_message)

            send_mail(
                subject="GrantU OTP Verification",
                message=plain_message,
                from_email="noreply@otp.com",
                recipient_list=[user.Email_Address],
                html_message=html_message,
            )

            token = generate_token(user)
            return Response({'token': token, 'verified': False}, status=status.HTTP_201_CREATED)

        elif user and len(password)!=0 and password == user.Password and user.is_verified:
            token = generate_token(user)
            return Response({'token': token, 'verified': True, 'is_mentor': user.is_mentor}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterVerify(APIView):
    authentication_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        email = user.Email_Address
        otp = request.data.get('otp')


        if user.is_verified == True:
            return Response({'msg': ' user already verified'}, status=400)
        if not otp:
            return Response({'error': ' OTP is required'}, status=400)  
        try:
            record = EmailOTP.objects.get(email=user)
        except EmailOTP.DoesNotExist:
            return Response({'error': 'user not found'}, status=404)

        if record.otp != otp:
            return Response({'error': 'Invalid OTP'}, status=400)

  

        user.is_verified = True
        user.save()
        return Response({'message': 'User registered successfully ✅'})


class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not all([email, otp, new_password]):
            return Response({'error': 'Email, OTP and new password are required'}, status=400)

        try:
            user = UserDetails.objects.get(Email_Address=email)
        except UserDetails.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        try:
            record = EmailOTP.objects.get(email=user)
        except EmailOTP.DoesNotExist:
            return Response({'error': 'OTP not found'}, status=404)

        if record.otp != otp:
            return Response({'error': 'Invalid OTP'}, status=400)

        if (timezone.now() - record.created_at).total_seconds() > 300:
            return Response({'error': 'OTP expired'}, status=400)

        user.Password = new_password  # or use make_password(new_password) if hashed
        user.save()
        record.delete()

        return Response({'message': 'Password reset successfully ✅'}, status=200)

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({'error': 'Email is required'}, status=400)

        try:
            user = UserDetails.objects.get(Email_Address=email)
        except UserDetails.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(
            email=user,
            defaults={"otp": otp, "created_at": timezone.now()}
        )

        send_mail(
            subject="Reset OTP",
            message=f"Your OTP is: {otp}",
            from_email="noreply@otp.com",
            recipient_list=[user.Email_Address]
        )

        return Response({'message': 'OTP sent successfully'}, status=200)
class VerifyResetOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not all([email, otp]):
            return Response({'error': 'Email and OTP are required'}, status=400)

        try:
            user = UserDetails.objects.get(Email_Address=email)
            record = EmailOTP.objects.get(email=user)
        except:
            return Response({'error': 'User or OTP not found'}, status=404)

        if record.otp != otp:
            return Response({'error': 'Invalid OTP'}, status=400)


        return Response({'message': 'OTP verified. Now set new password'}, status=200)
class SetNewPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if not all([email, password, confirm_password]):
            return Response({'error': 'All fields required'}, status=400)

        if password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=400)

        try:
            user = UserDetails.objects.get(Email_Address=email)
        except UserDetails.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        user.Password = password  # or make_password(password)
        user.save()

        # Clean up old OTPs
        EmailOTP.objects.filter(email=user).delete()

        # 🔥 Generate new token after password reset
        token = generate_token(user)

        return Response({
            'message': 'Password updated successfully ✅',
            'token': token
        }, status=200)

