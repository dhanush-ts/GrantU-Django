from django.shortcuts import render
from rest_framework import generics
from .models import Connection, FreeTimeSlots, GmeetSchedule
from .serializers import ConnectionSerializer, FreeTimeSlotSerializer, GmeetScheduleSerializer
from users.authentication import IsAuthenticated
from rest_framework.response import Response
from user_auth.permission import IsOwner
from rest_framework import status
from rest_framework.views import APIView
from django.template.loader import render_to_string
from collections import defaultdict, OrderedDict
from user_auth.permission import ConnectionOwner
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from django.core.mail import EmailMessage
from datetime import timedelta
from users.serializer import *

# Create your views here.
class ConnectionCreateView(generics.CreateAPIView):
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer
    authentication_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class FreeTimeSlotView(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get("id")
        if user_id:
            try:
                user = UserDetails.objects.get(User_ID=user_id)
            except UserDetails.DoesNotExist:
                return Response({"error": "User not found."}, status=404)
        else:
            user = request.user
        slots = FreeTimeSlots.objects.filter(User=user)
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        grouped = defaultdict(list)

        for slot in slots:
            day = slot.Day.capitalize()
            serialized = FreeTimeSlotSerializer(slot).data
            grouped[day].append(serialized)

        result = OrderedDict()
        for day in day_order:
            result[day] = grouped.get(day, [])
        return Response(result)

    def post(self, request):
        serializer = FreeTimeSlotSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Slot created successfully", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)

class GmeetScheduleView(APIView):
    authentication_classes = [IsAuthenticated]
    permission_classes = [ConnectionOwner]

    def post(self, request):
        Connection_id = request.data.get("Connection")
        if not Connection_id:
            return Response({"error": "Connection_id is required"}, status=400)

        try:
            Connect = Connection.objects.get(pk=Connection_id)
        except Connection.DoesNotExist:
            return Response({"error": "Connection not found"}, status=404)
        self.check_object_permissions(request, Connect)

        start_time_str = request.data.get("Meeting_Start_Time")
        end_time_str = request.data.get("Meeting_End_Time")

        if not start_time_str or not end_time_str:
            return Response({"error": "Meeting_Start_Time and Meeting_End_Time are required"}, status=400)

        start_dt = parse_datetime(start_time_str)
        end_dt = parse_datetime(end_time_str)

        free_slots = FreeTimeSlots.objects.filter(User=Connect.Mentor, Day=start_dt.strftime('%A'))

        within_slot = False
        for slot in free_slots:
            if slot.Start_Time <= start_dt.time() and slot.End_Time >= end_dt.time():
                within_slot = True
                break

        if not within_slot and not Connect.Mentor == request.user:
            return Response({"error": "No free time slot available for the mentor during this period."}, status=400)

        if end_dt - start_dt < timedelta(minutes=15):
            return Response({"error": "Meeting must be at least 15 minutes long."}, status=400)

        start_dt = parse_datetime(start_time_str) - timedelta(hours=5, minutes=30)
        end_dt = parse_datetime(end_time_str) - timedelta(hours=5, minutes=30)

        overlapping_meetings = GmeetSchedule.objects.filter(
            Q(Connection__Mentor=Connect.Mentor) | Q(Connection__Mentee=Connect.Mentor),
            Meeting_Start_Time__lt=end_dt,
            Meeting_End_Time__gt=start_dt
        )

        todays_Connections = GmeetSchedule.objects.filter(
            Q(Connection__Mentor=Connect.Mentor) | Q(Connection__Mentee=Connect.Mentor),
            Meeting_Start_Time__date=start_dt.date()
        ).order_by('Meeting_Start_Time')

        if overlapping_meetings.exists():
            serialized = GmeetScheduleSerializer(todays_Connections, many=True).data
            return Response({
                "error": "Mentor not available at this time.",
                "todays_bookings": serialized
            }, status=203)

        # Save meeting
        serializer = GmeetScheduleSerializer(data=request.data)
        if serializer.is_valid():
            schedule = serializer.save()
            return Response({
                "message": "Meeting scheduled",
                "meeting_link": schedule.Meeting_Link,
                "start": schedule.Meeting_Start_Time,
                "end": schedule.Meeting_End_Time,
                "description": schedule.Description
            }, status=201)

        return Response(serializer.errors, status=400)
    
    def get(self, request):
        user = request.user
        Connections = Connection.objects.filter(Mentor=user) | Connection.objects.filter(Mentee=user)
        schedules = GmeetSchedule.objects.filter(Connection__in=Connections).order_by('Meeting_Start_Time')

        now = timezone.now()

        # Separate into upcoming and completed
        upcoming_schedules = schedules.filter(Meeting_End_Time__gte=now)
        completed_schedules = schedules.filter(Meeting_End_Time__lt=now)

        # Serialize separately
        upcoming_data = GmeetScheduleSerializer(upcoming_schedules, many=True).data
        completed_data = GmeetScheduleSerializer(completed_schedules, many=True).data

        return Response({
            "upcoming": upcoming_data,
            "completed": completed_data
        }, status=200)
        
class GetMentorRequest(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        accepted_only = request.query_params.get('accepted_only') == 'true'
        
        Connections = Connection.objects.filter(Mentor=user)
        if accepted_only:
            Connections = Connections.filter(status='accepted')
        
        serializer = ConnectionSerializer(Connections, many=True, context={"request": request})
        return Response({'data': serializer.data})


class GetMenteeRequest(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        accepted_only = request.query_params.get('accepted_only') == 'true'
        
        Connections = Connection.objects.filter(Mentee=user)
        if accepted_only:
            Connections = Connections.filter(status='accepted')
        
        serializer = ConnectionSerializer(Connections, many=True, context={"request": request})
        return Response({'data': serializer.data})

class AcceptRequest(APIView):
    authentication_classes = [IsAuthenticated]
    permission_classes = [IsOwner]

    def post(self, request, Connection_id):
        user = request.user
        try:
            Connect = Connection.objects.get(Connection_ID=Connection_id)
        except Connection.DoesNotExist:
            return Response({'error': 'Invalid Connection id'}, status=404)

        Connect.status = "accepted"
        Connect.save()

        # Get mentor and mentee names
        mentor_name = Connect.Mentor.First_Name + " " + Connect.Mentor.Last_Name
        mentee_name = Connect.Mentee.First_Name + " " + Connect.Mentee.Last_Name

        # Render email
        email_html = render_to_string("request_accepted_email.html", {
            "mentor_name": mentor_name,
            "mentee_name": mentee_name
        })
        
        sender_list = []
        if Connect.Selection_By == "mentor":
            sender_list.append(Connect.Mentor.Email_Address)
        else:
            sender_list.append(Connect.Mentee.Email_Address)

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

    def delete(self, request, Connection_id):
        user = request.user
        try:
            Connect = Connection.objects.get(Connection_ID=Connection_id)
        except Connection.DoesNotExist:
            return Response({'error': 'Invalid Connection id'}, status=404)
        if Connect.status != "pending":
            return Response({'error': 'Connection is not in pending status'}, status=400)
        self.check_object_permissions(request, Connect)
        Connect.status = "rejected"
        Connect.save()
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
                Connect = Connection.objects.get(Mentor=another_user, Mentee=user, status='pending')
            elif user_type == 'mentor':
                Connect = Connection.objects.get(Mentor=user, Mentee=another_user, status='pending')
        except Connection.DoesNotExist:
            return Response({'error': 'Invalid Connection id'}, status=404)

        Connect.status = "accepted"
        Connect.save()

        # Get mentor and mentee names
        mentor_name = Connect.Mentor.First_Name + " " + Connect.Mentor.Last_Name
        mentee_name = Connect.Mentee.First_Name + " " + Connect.Mentee.Last_Name

        # Render email
        email_html = render_to_string("request_accepted_email.html", {
            "mentor_name": mentor_name,
            "mentee_name": mentee_name
        })
        
        sender_list = []
        if Connect.Selection_By == "mentor":
            sender_list.append(Connect.Mentor.Email_Address)
        else:
            sender_list.append(Connect.Mentee.Email_Address)

        # Send email to mentee
        email = EmailMessage(
            subject="Your request was accepted!",
            body=email_html,
            to=sender_list,
        )
        email.content_subtype = "html"
        email.send(fail_silently=True)

        return Response({"detail": "accepted successfully"})