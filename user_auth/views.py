from django.shortcuts import render
from .permission import IsOwner
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import EmailOTP
import random
from rest_framework import status
from users.serializer import *
from users.authentication import *
from rest_framework import generics, mixins
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMessage

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

        if user and password == user.Password and not user.is_verified:
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

        elif user and password == user.Password and user.is_verified:
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

class GetMentorRequest(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        accepted_only = request.query_params.get('accepted_only') == 'true'
        
        bookings = Booking.objects.filter(Mentor=user)
        if accepted_only:
            bookings = bookings.filter(status='accepted')
        
        serializer = BookingSerializer(bookings, many=True, context={"request": request})
        return Response({'data': serializer.data})


class GetMenteeRequest(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        accepted_only = request.query_params.get('accepted_only') == 'true'
        
        bookings = Booking.objects.filter(Mentee=user)
        if accepted_only:
            bookings = bookings.filter(status='accepted')
        
        serializer = BookingSerializer(bookings, many=True, context={"request": request})
        return Response({'data': serializer.data})

class AcceptRequest(APIView):
    authentication_classes = [IsAuthenticated]
    permission_classes = [IsOwner]

    def post(self, request, booking_id):
        user = request.user
        try:
            booking = Booking.objects.get(Booking_ID=booking_id)
        except Booking.DoesNotExist:
            return Response({'error': 'Invalid booking id'}, status=404)

        booking.status = "accepted"
        booking.save()

        # Get mentor and mentee names
        mentor_name = booking.Mentor.First_Name + " " + booking.Mentor.Last_Name
        mentee_name = booking.Mentee.First_Name + " " + booking.Mentee.Last_Name

        # Render email
        email_html = render_to_string("request_accepted_email.html", {
            "mentor_name": mentor_name,
            "mentee_name": mentee_name
        })
        
        sender_list = []
        if booking.Selection_By == "mentor":
            sender_list.append(booking.Mentor.Email_Address)
        else:
            sender_list.append(booking.Mentee.Email_Address)

        # Send email to mentee
        email = EmailMessage(
            subject="Your request was accepted!",
            body=email_html,
            to=sender_list,
        )
        email.content_subtype = "html"
        email.send(fail_silently=True)

        return Response({"detail": "accepted successfully"})
    
class RejectRequest(APIView):
    authentication_classes = [IsAuthenticated]
    permission_classes = [IsOwner]

    def delete(self, request, booking_id):
        user = request.user
        try:
            booking = Booking.objects.get(Booking_ID=booking_id)
        except Booking.DoesNotExist:
            return Response({'error': 'Invalid booking id'}, status=404)
        if booking.status != "pending":
            return Response({'error': 'Booking is not in pending status'}, status=400)
        self.check_object_permissions(request, booking)
        booking.status = "rejected"
        booking.save()
        return Response({"detail": "rejected successfully"})
    
class ListOfStudents(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        students = UserDetails.objects.all().exclude(User_ID=user.User_ID)
        serializer = UserBasicDetailsSerializer(students, many=True, context={"request": request})
        return Response({'students': serializer.data}, status=200)
    
    
class AcceptRequestUser(APIView):
    authentication_classes = [IsAuthenticated]
    permission_classes = [IsOwner]

    def post(self, request, user_id):
        user_type = request.query_params.get('type')
        user = request.user
        try:
            another_user = UserDetails.objects.get(User_ID=user_id)
            if user_type == 'mentee':
                booking = Booking.objects.get(Mentor=another_user, Mentee=user, status='pending')
            elif user_type == 'mentor':
                booking = Booking.objects.get(Mentor=user, Mentee=another_user, status='pending')
        except Booking.DoesNotExist:
            return Response({'error': 'Invalid booking id'}, status=404)

        booking.status = "accepted"
        booking.save()

        # Get mentor and mentee names
        mentor_name = booking.Mentor.First_Name + " " + booking.Mentor.Last_Name
        mentee_name = booking.Mentee.First_Name + " " + booking.Mentee.Last_Name

        # Render email
        email_html = render_to_string("request_accepted_email.html", {
            "mentor_name": mentor_name,
            "mentee_name": mentee_name
        })
        
        sender_list = []
        if booking.Selection_By == "mentor":
            sender_list.append(booking.Mentor.Email_Address)
        else:
            sender_list.append(booking.Mentee.Email_Address)

        # Send email to mentee
        email = EmailMessage(
            subject="Your request was accepted!",
            body=email_html,
            to=sender_list,
        )
        email.content_subtype = "html"
        email.send(fail_silently=True)

        return Response({"detail": "accepted successfully"})