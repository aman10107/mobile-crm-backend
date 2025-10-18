from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import LoginRequestSerializer, OTPVerificationModelSerializer, LoginVerificationSerializer
from  userApp.serializers import UserSerializer, UserDetailsSerializer
from rest_framework import status
from .models import OTPVerificationModel
from  django.contrib.auth.models import User
from userApp.models import UserDetailsModel
from helpers import EmailHelper
import uuid
from shopApp.serializers import ShopDetailsModelSerializer


class LoginRequestAPIView(APIView):
    authentication_classes = []
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"message" : serializer.error_messages, "details" :serializer.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        otp = OTPVerificationModel.generate_otp()
        email =  serializer.data["email"]
        password = serializer.data["password"]
        subject = "Registration OTP"
        message = f"This is a OTP for registration at app {otp}"
        if User.objects.filter(username=email).exists():
            subject = "Login OTP"
            message = f"This is a OTP for Login at app {otp}"
            if password:
                from django.contrib.auth import authenticate
                from rest_framework_simplejwt.tokens import RefreshToken
                user = authenticate(request, username=email, password=password)
                if user is None:
                    return Response({"detail": "Invalid credentials."},
                                    status=status.HTTP_401_UNAUTHORIZED)
                refresh = RefreshToken.for_user(user)
                access = refresh.access_token

                return Response({
                    "refresh": str(refresh),
                    "access": str(access),
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    }
                }, status=status.HTTP_202_ACCEPTED)

                
        if EmailHelper.sendMail(email, message, subject):
            token = uuid.uuid4()
            otpSerializer = OTPVerificationModelSerializer(data={
                "token" : token,
                "otp_method" : OTPVerificationModel.OTPMethods.EMAIL,
                "otp_value" : otp,
                "purpose" : OTPVerificationModel.Purposes.LOGIN,
                "email" : email
            })
            if otpSerializer.is_valid():
                otpSerializer.save()
                return Response(
                    {
                        "token" : token
                    }, 
                    status=status.HTTP_200_OK
                    )
            else :
                return Response(otpSerializer.errors)
        return Response({"message" : "Error while sending mail, please retry", "detail":"Error while sending mail to the givn mail"})


class LoginVerificationAPIView(APIView):
    authentication_classes = []

    def post(self, request):
        print("1")
        serializer = LoginVerificationSerializer(data=request.data)
        print("2")
        if not serializer.is_valid():
            print("3")
            return Response({"message":"Please enter valida values", "detail":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        print("4")
        token = serializer.data['token']
        otp = serializer.data['otp']
        password = serializer.data['password']
        if not OTPVerificationModel.objects.filter(token=token, otp_value=otp, otp_method=OTPVerificationModel.OTPMethods.EMAIL, purpose=OTPVerificationModel.Purposes.LOGIN).exists():
            print("5")
            return Response({"message" : "Invalid / expired OTP"}, status=status.HTTP_401_UNAUTHORIZED)
        otpModel = OTPVerificationModel.objects.get(token=token)
        email = otpModel.email
        if not User.objects.filter(username=email).exists():
            print("6")
            print("user does not exist")
            print("password is", password)
            userSerializer = UserSerializer(data={"username":email, "email" : email, "password":password})
            if not userSerializer.is_valid():
                return Response({"message":"User can't be created.", "detail":serializer.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            user = userSerializer.save()
            print(user)
            user.set_password(password)
            user.save()
            userDetailsSerializer = UserDetailsSerializer(data={
                "user" : user.id
            })
            shopDetailsErializer = ShopDetailsModelSerializer(data={
                "owner" : user.id,
                "name" : "New Shop"
            })
            if not userDetailsSerializer.is_valid():
                return Response({"message":"Invalid user details backed issue", "detail":serializer.error_messages}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            userDetailsSerializer.save()
            if not shopDetailsErializer.is_valid():
                return Response({"message":"Something went wrong !!", "detail":serializer.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            shopDetailsErializer.save()

            from django.contrib.auth import authenticate
            from rest_framework_simplejwt.tokens import RefreshToken
            user = authenticate(request, username=email, password=password)
            if user is None:
                return Response({"detail": "Invalid credentials."},
                                status=status.HTTP_401_UNAUTHORIZED)
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
        
            return Response({
                "user_details":userDetailsSerializer.data,
                "message" : "Registered sucessfully",
                "refresh" : str(refresh),
                "access" : str(access)
                }, status=status.HTTP_200_OK)
        
        else :
            user = User.objects.get(username=email)
            userDetails = UserDetailsModel.objects.get(user=user)
            userDetailsSerializer = UserDetailsSerializer(userDetails)

            # Generate access token
            from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
            access_token = AccessToken.for_user(user)
            # Generate refresh token
            refresh_token = RefreshToken.for_user(user)

            return Response(
                {
                    "messgae" : "Logged in Sucessfuly",
                    "data" : {
                        "user_details": userDetailsSerializer.data,
                        "access" : str(access_token),
                        "refresh" : str(refresh_token)
                    }
                },
                status = status.HTTP_200_OK
            )
            
