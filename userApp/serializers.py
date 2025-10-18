from rest_framework import serializers
from  customCalsses.CustomBaseModelSerializer import CustomBaseModelSerializer
from django.contrib.auth.models import User
from .models import UserDetailsModel
from shopApp.models import ShopDetailsModel
from shopApp.serializers import ShopDetailsModelSerializer
from rest_framework.response import Response
from  rest_framework import status

class UserSerializer(CustomBaseModelSerializer):
    class Meta:
        model = User
        # fields = "__all__"
        exclude = ['password']

class UserDetailsSerializer(CustomBaseModelSerializer):
    shops = serializers.SerializerMethodField()
    class Meta:
        model = UserDetailsModel
        fields = "__all__"

    def get_shops(self, obj):
        user = obj.user
        shops = ShopDetailsModel.objects.filter(owner=user)
        shopsDetails = ShopDetailsModelSerializer(shops, many=True)
        return shopsDetails.data
