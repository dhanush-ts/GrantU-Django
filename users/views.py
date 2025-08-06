import random
from rest_framework import generics
from .models import UserDetails
from .serializer import *
from .authentication import IsAuthenticated, generate_token
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from .models import Interest
from django.shortcuts import get_object_or_404

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


class InterestListView(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request):
        interests = Interest.objects.all().values_list('name', flat=True)
        return Response(list(interests))