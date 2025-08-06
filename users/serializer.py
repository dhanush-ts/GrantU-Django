from rest_framework import serializers
from .models import *
from connections.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = [
            'First_Name',
            'Last_Name',
            'Email_Address',
            'Phone_Number',
            'Password',
            'pincode',
            'address',
            'DOB',
            'Gender',
            'Expertise',
            'Field_of_Interest', 
            'Requirements'
            ,'Years_of_Experience'
            ,'organization_detail'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
        
        
class UserBasicDetailsSerializer(serializers.ModelSerializer):
    your_student = serializers.SerializerMethodField()
    request_pending = serializers.SerializerMethodField()
    your_mentor = serializers.SerializerMethodField()
    can_accept = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = UserDetails
        fields = ['User_ID', 'First_Name', 'Last_Name','Expertise','Field_of_Interest','Requirements','organization_detail', 'your_student', 'your_mentor', 'request_pending', 'can_accept']
        
    def get_your_student(self, obj):
        user = self.context['request'].user
        return Connection.objects.filter(Mentor=user, Mentee=obj, status='accepted').exists()
    
    def get_can_accept(self, obj):
        request = self.context['request']
        user = request.user
        user_type = request.query_params.get('type')
        if user_type == 'mentor':
            return Connection.objects.filter(Mentor=obj, Mentee=user, status='pending',Selection_By="mentor").exists()
        
        elif user_type == 'mentee':
            return Connection.objects.filter(Mentor=user, Mentee=obj, status='pending',Selection_By="mentee").exists()
        return False

    def get_your_mentor(self, obj):
        user = self.context['request'].user
        return Connection.objects.filter(Mentor=obj, Mentee=user, status='accepted').exists()

    def get_request_pending(self, obj):
        user = self.context['request'].user
        return Connection.objects.filter(Mentor__in=[user,obj], Mentee__in=[obj,user], status='pending').exists()

class UserFieldUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ['Field_of_Interest', 'Requirements']  # Only allow these fields
    
class ExpertFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ['Expertise','Years_of_Experience','organization_detail']  # Only allow these fields

class ProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = [  'pincode', 'address']  # Only allow these fields