from rest_framework import serializers
from customCalsses.CustomBaseModelSerializer import CustomBaseModelSerializer
from .models import OTPVerificationModel

class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password  =  serializers.CharField(max_length=40, min_length=10, required=False)

class OTPVerificationModelSerializer(CustomBaseModelSerializer):
    class Meta:
        model = OTPVerificationModel
        fields = "__all__"
    
class LoginVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=600, required=True)
    otp = serializers.CharField(max_length=4, min_length=4, required=True)
    password = password  =  serializers.CharField(max_length=40, min_length=10, required=False)

