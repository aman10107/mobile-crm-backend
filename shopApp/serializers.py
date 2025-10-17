
# from rest_framework import serializers
from customCalsses.CustomBaseModelSerializer import CustomBaseModelSerializer
from .models import ShopDetailsModel

class ShopDetailsModelSerializer(CustomBaseModelSerializer):

    class Meta:
        model = ShopDetailsModel
        fields = "__all__"