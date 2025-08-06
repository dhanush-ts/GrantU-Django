from rest_framework import serializers
from .models import Connection, FreeTimeSlots, GmeetSchedule
from users.models import UserDetails, Interest
from users.serializer import UserBasicDetailsSerializer
from django.utils import timezone
from datetime import timedelta

class ConnectionSerializer(serializers.ModelSerializer):
    Interests = serializers.ListField(
        child=serializers.CharField(),
        write_only=True
    )
    Interests_names = serializers.SerializerMethodField(read_only=True)
    can_accept = serializers.SerializerMethodField(read_only=True)
    Mentor = UserBasicDetailsSerializer(read_only=True)
    Mentee = UserBasicDetailsSerializer(read_only=True)

    class Meta:
        model = Connection
        fields = [
            'Connection_ID',
            'Mentor',
            'Mentee',
            'Description',
            'Details',
            'Selection_By',
            'Interests',
            'Interests_names',
            'status',
            'can_accept',
            'created_at'
        ]
        read_only_fields = ['Mentor', 'Mentee','status','created_at']
        
    def get_can_accept(self, obj):
        user = self.context['request'].user
        if (
            obj.status == 'pending' and
            (
                (user == obj.Mentor and obj.Selection_By != "mentor") or
                (user == obj.Mentee and obj.Selection_By != "mentee")
            )
        ):
            return True
        return False

    def get_Interests_names(self, obj):
        return [interest.name for interest in obj.Interests.all()]

    def create(self, validated_data):
        request = self.context['request']
        connection_type = request.data.get('Selection_By', '').lower()
        user_details = request.user
        interests_names = validated_data.pop('Interests', [])

        if connection_type == "mentor":
            mentee_id = request.data.get('Mentee')
            if not mentee_id:
                raise serializers.ValidationError({"Mentee": "This field is required when type is 'mentor'."})
            try:
                mentee = UserDetails.objects.get(User_ID=mentee_id)
            except UserDetails.DoesNotExist:
                raise serializers.ValidationError({"Mentee": "User not found."})
            mentor = user_details
        elif connection_type == "mentee":
            mentor_id = request.data.get('Mentor')
            if not mentor_id:
                raise serializers.ValidationError({"Mentor": "This field is required when type is 'mentee'."})
            try:
                mentor = UserDetails.objects.get(User_ID=mentor_id)
            except UserDetails.DoesNotExist:
                raise serializers.ValidationError({"Mentor": "User not found."})
            mentee = user_details
        else:
            raise serializers.ValidationError({"type": "Must be either 'mentor' or 'mentee'"})
        
        
        cutoff_date = timezone.now() - timedelta(days=60)

        previously_booked = Connection.objects.filter(
            Mentor=mentor,
            Mentee=mentee,
            created_at__gt=cutoff_date,
            Selection_By=connection_type
        )
        
        if previously_booked.exists():
            raise serializers.ValidationError("This mentor-mentee pair has already booked a session in the last 60 days.")
        conn = Connection.objects.create(
            Mentor=mentor,
            Mentee=mentee,
            **validated_data
        )

        interests = Interest.objects.filter(name__in=interests_names)
        conn.Interests.set(interests)

        return conn

    def validate(self, data):
        user = self.context['request'].user
        user_type = self.context['request'].data.get('Selection_By')  # e.g., "mentor" or "mentee"
        
        if user_type == "mentor":
            mentor = user
            mentee_id = self.context['request'].data.get('Mentee')
            mentee = UserDetails.objects.get(User_ID=mentee_id)
        elif user_type == "mentee":
            mentee = user
            mentor_id = self.context['request'].data.get('Mentor')
            mentor = UserDetails.objects.get(User_ID=mentor_id)
        else:
            raise serializers.ValidationError("Invalid user type.")

        # Check limits
        if Connection.objects.filter(Mentor=mentor,status="accepted").count() >= 3:
            raise serializers.ValidationError("This mentor already has 3 mentees.")
        
        if Connection.objects.filter(Mentee=mentee,status="accepted").count() >= 5:
            raise serializers.ValidationError("This mentee already has 5 mentors.")
        
        return data
    
class StudentSerializer(serializers.ModelSerializer):
    your_student = serializers.SerializerMethodField()
    request_pending = serializers.SerializerMethodField()
    your_mentor = serializers.SerializerMethodField()

    class Meta:
        model = UserDetails
        fields = ['User_ID', 'First_Name', 'Last_Name', 'Email_Address', 'Phone_Number', 'your_student', 'your_mentor', 'request_pending']

    def get_your_student(self, obj):
        user = self.context['request'].user
        return Connection.objects.filter(Mentor=user, Mentee=obj, status='accepted').exists()

    def get_your_mentor(self, obj):
        user = self.context['request'].user
        return Connection.objects.filter(Mentor=obj, Mentee=user, status='accepted').exists()

    def get_request_pending(self, obj):
        user = self.context['request'].user
        return Connection.objects.filter(Mentor__in=[user,obj], Mentee__in=[obj,user], status='pending').exists()
    
class FreeTimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeTimeSlots
        fields = ['id', 'Day', 'Start_Time', 'End_Time', 'Created_At']
        
    def create(self, validated_data):
        validated_data['User'] = self.context['request'].user
        return super().create(validated_data)

class GmeetScheduleSerializer(serializers.ModelSerializer):
    Mentee = serializers.SerializerMethodField(read_only=True)
    Mentor = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = GmeetSchedule
        read_only_fields = ['Mentee', 'Mentor']
        fields = ['Connection', 'Meeting_Start_Time', 'Meeting_End_Time', 'Meeting_Link', 'Mentee', 'Mentor','Description']

    def create(self, validated_data):
        from django.conf import settings
        from utils.helper import Helper 

        conn = validated_data['Connection']
        start = validated_data['Meeting_Start_Time']
        end = validated_data['Meeting_End_Time']
        description = validated_data['Description']
        
        start = start - timedelta(hours=5, minutes=30)
        end = end - timedelta(hours=5, minutes=30)
    
        link = Helper.create_gmeet_link(self,conn, start, end, description)

        return GmeetSchedule.objects.create(
            Connection=conn,
            Meeting_Link=link,
            Meeting_Start_Time=start,
            Meeting_End_Time=end,
            Description=description
        )
        
    def get_Mentee(self, obj):
        return obj.Connection.Mentee.First_Name if obj.Connection.Mentee else None
    def get_Mentor(self, obj):
        return obj.Connection.Mentor.First_Name if obj.Connection.Mentor else None