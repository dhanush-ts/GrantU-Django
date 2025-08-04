import random
from rest_framework import generics
from .models import UserDetails
from .serializer import *
from .authentication import IsAuthenticated, generate_token
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.conf import settings
from rest_framework.response import Response
from rest_framework import generics
from .models import Booking,Interest
from user_auth.views import GetMentorRequest,GetMenteeRequest
from .serializer import BookingSerializer
from django.shortcuts import get_object_or_404
from collections import defaultdict, OrderedDict
from user_auth.permission import BookingOwner
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive
from datetime import timedelta, timezone
import pytz



class UserListView(generics.ListCreateAPIView):
    queryset = UserDetails.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [IsAuthenticated]



class ProfileView(APIView):
    authentication_classes = [IsAuthenticated]


    def get(self, request):
        serializer = UserSerializer(request.user)
        data = serializer.data
        data['is_mentor'] = request.user.is_mentor  # Add the new key here
        return Response(data)  # Assuming you're returning a response
    
class Fieldofinterest(APIView):
    authentication_classes = [IsAuthenticated]  # Your custom one
    

    def patch(self, request):
        print("User:", request.user)
        print("Is Authenticated:", request.user.is_authenticated)
        print("Is Staff:", request.user.is_staff)

        user = request.user
        user_details = get_object_or_404(UserDetails, Email_Address=user.Email_Address)

        raw_interests = request.data.get("Field_of_Interest", [])
        requirements = request.data.get("Requirements", "")

        # 🧠 Smart alias-to-label mapping
        mapping = {
            # 🔹 TECH FIELDS
            "Artificial Intelligence": ["ai", "artificial", "artificial intelligence", "machine intel"],
            "Machine Learning": ["ml", "machine learning", "supervised", "unsupervised", "ml engineer"],
            "Deep Learning": ["dl", "deep learning", "neural network", "cnn", "rnn", "transformers"],
            "Data Science": ["ds", "data science", "data analysis", "eda", "data viz"],
            "Data Engineering": ["etl", "pipeline", "data engineer", "big data", "airflow"],
            "Computer Vision": ["cv", "image processing", "object detection", "opencv"],
            "Natural Language Processing": ["nlp", "text processing", "bert", "gpt", "language model"],
            "DevOps": ["devops", "ci/cd", "docker", "kubernetes", "k8s", "ansible"],
            "Cloud Computing": ["cloud", "aws", "azure", "gcp", "cloud engineer", "cloud services"],
            "Cybersecurity": ["cybersecurity", "infosec", "hacking", "penetration testing", "burpsuite"],
            "Blockchain": ["blockchain", "crypto", "ethereum", "web3", "nft", "solidity"],
            "Internet of Things": ["iot", "smart devices", "sensor", "embedded systems"],
            "Frontend Development": ["frontend", "html", "css", "js", "javascript", "react", "vue", "angular"],
            "Backend Development": ["backend", "django", "flask", "nodejs", "api", "rest"],
            "Full Stack Development": ["fullstack", "mern", "mean", "web dev"],
            "Mobile App Development": ["android", "ios", "flutter", "react native", "kotlin", "swift"],
            "Game Development": ["game dev", "unity", "unreal", "gamedev", "level design"],
            "Database Management": ["db", "sql", "nosql", "mongodb", "postgres", "oracle", "mysql"],
            "Software Engineering": ["software", "coding", "sde", "development"],
            "UI/UX Design": ["ui", "ux", "figma", "design", "user interface", "user experience"],
            "Robotics": ["robotics", "ros", "arduino", "automation"],
            "Augmented/Virtual Reality": ["ar", "vr", "virtual reality", "augmented", "xr", "metaverse"],
            "Big Data": ["big data", "hadoop", "spark", "data lake"],
            "Quantum Computing": ["quantum", "qiskit", "quantum computing"],
            "Networking": ["network", "tcp", "ip", "ccna", "firewall", "dns"],
            "Operating Systems": ["linux", "os", "windows kernel", "system programming"],

            # 🔹 CREATIVE + ARTS
            "Photography": ["photography", "camera", "dslr", "photo editing", "lightroom", "portrait", "wildlife"],
            "Graphic Design": ["graphic design", "photoshop", "illustrator", "coreldraw", "canva"],
            "Video Editing": ["video edit", "premiere", "after effects", "film making", "davinci", "reels"],
            "Music Production": ["music", "beat making", "fl studio", "logic pro", "composer", "sound design"],
            "Writing & Content": ["writing", "blogging", "creative writing", "copywriting", "author", "novel"],
            "Digital Marketing": ["marketing", "seo", "sem", "social media", "influencer", "ads"],

            # 🔹 EDUCATION & HUMANITIES
            "Psychology": ["psychology", "mind", "mental", "therapy", "counseling"],
            "Philosophy": ["philosophy", "thinking", "existence", "logic", "ethics"],
            "Education": ["teacher", "education", "learning", "tutor", "pedagogy", "training"],
            "Sociology": ["society", "culture", "social work", "human behavior", "sociology"],
            "History": ["history", "ancient", "war", "civilization", "historical"],

            # 🔹 BUSINESS & FINANCE
            "Entrepreneurship": ["startup", "entrepreneur", "founder", "business", "venture"],
            "Finance": ["finance", "investment", "stocks", "trading", "money", "banking"],
            "Economics": ["economics", "macro", "micro", "policy", "economic theory"],
            "Law": ["law", "legal", "lawyer", "court", "case", "justice"],

            # 🔹 OTHERS
            "Environmental Science": ["environment", "climate", "sustainability", "eco", "green"],
            "Biotechnology": ["bio", "biotech", "genetics", "bioinformatics"],
            "Civil Engineering": ["civil", "construction", "structures", "bridge", "road"],
            "Mechanical Engineering": ["mechanical", "machines", "automobile", "thermodynamics"],
            "Electrical Engineering": ["electrical", "circuit", "power", "eectronics", "vlsi"],}

        cleaned_interests = []
        for raw in raw_interests:
            raw_lower = raw.strip().lower()
            matched = False
            for label, aliases in mapping.items():
                if any(raw_lower in alias for alias in aliases):
                    cleaned_interests.append(label)
                    matched = True
                    break
            if not matched:
                cleaned_interests.append(raw.strip())

        # Save to user model
        user_details.Field_of_Interest = cleaned_interests
        user_details.Requirements = requirements
        user_details.save()

        return Response({
            "message": "Field of Interest updated ✅",
            "Field_of_Interest": cleaned_interests,
            "Requirements": requirements
        }, status=status.HTTP_200_OK)

class ExpertField(APIView):
    authentication_classes = [IsAuthenticated]

    def patch(self, request):

        user = request.user
        user_details = get_object_or_404(UserDetails, Email_Address=user.Email_Address)
        serializer = ExpertFieldSerializer(user_details, data=request.data, partial=True)
        
        if serializer.is_valid():
            user_details.Expertise = request.data.get('Expertise', [])
            user_details.Years_of_Experience = request.data.get('Years_of_Experience', '')
            user_details.organization_detail = request.data.get('organization_detail', '')

            user_details.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileUpdate(APIView):
    authentication_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user

        user_details = get_object_or_404(UserDetails, Email_Address=user.Email_Address)

        serializer = ProfileEditSerializer(user_details, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MentorList(APIView):
    def get(self,request):
        user = request.user
        users = UserDetails.objects.filter(organization_detail__isnull=False)
        details = UserSerializer(users,many=True)
        return Response(details.data,status=status.HTTP_200_OK)

class Metrics(APIView):
    def get(self,request):
        count_stus = UserDetails.objects.all().count()
        count_ments = UserDetails.objects.filter(organization_detail__isnull=False).count()
        return Response({"students":count_stus, "ments":count_ments})

class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    authentication_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class InterestListView(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request):
        interests = Interest.objects.all().values_list('name', flat=True)
        return Response(list(interests))
    
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
    
IST = timezone(timedelta(hours=5, minutes=30))

class GmeetScheduleView(APIView):
    authentication_classes = [IsAuthenticated]
    permission_classes = [BookingOwner]

    def post(self, request):
        booking_id = request.data.get("Booking")
        if not booking_id:
            return Response({"error": "booking_id is required"}, status=400)

        try:
            booking = Booking.objects.get(pk=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)
        self.check_object_permissions(request, booking)

        start_time_str = request.data.get("Meeting_Start_Time")
        end_time_str = request.data.get("Meeting_End_Time")

        if not start_time_str or not end_time_str:
            return Response({"error": "Meeting_Start_Time and Meeting_End_Time are required"}, status=400)

        start_dt = parse_datetime(start_time_str)
        end_dt = parse_datetime(end_time_str)

        if is_naive(start_dt):
            start_dt = make_aware(start_dt, timezone=IST)
        else:
            start_dt = start_dt.astimezone(IST)

        if is_naive(end_dt):
            end_dt = make_aware(end_dt, timezone=IST)
        else:
            end_dt = end_dt.astimezone(IST)

        free_slots = FreeTimeSlots.objects.filter(User=booking.Mentor, Day=start_dt.strftime('%A'))

        within_slot = False
        for slot in free_slots:
            if slot.Start_Time <= start_dt.time() and slot.End_Time >= end_dt.time():
                within_slot = True
                break

        if not within_slot and not booking.Mentor == request.user:
            return Response({"error": "No free time slot available for the mentor during this period."}, status=400)

        if end_dt - start_dt < timedelta(minutes=15):
            return Response({"error": "Meeting must be at least 15 minutes long."}, status=400)

        overlapping_meetings = GmeetSchedule.objects.filter(
            Q(Booking__Mentor=booking.Mentor) | Q(Booking__Mentee=booking.Mentor),
            Meeting_Start_Time__lt=end_dt,
            Meeting_End_Time__gt=start_dt
        )

        todays_bookings = GmeetSchedule.objects.filter(
            Q(Booking__Mentor=booking.Mentor) | Q(Booking__Mentee=booking.Mentor),
            Meeting_Start_Time__date=start_dt.date()
        ).order_by('Meeting_Start_Time')

        if overlapping_meetings.exists():
            serialized = GmeetScheduleSerializer(todays_bookings, many=True).data
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
        bookings = Booking.objects.filter(Mentor=user) | Booking.objects.filter(Mentee=user)
        schedules = GmeetSchedule.objects.filter(Booking__in=bookings).order_by('Meeting_Start_Time')

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