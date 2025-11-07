
# from rest_framework import serializers
from customCalsses.CustomBaseModelSerializer import CustomBaseModelSerializer
from .models import ShopDetailsModel, ShopPermissionsModel

class ShopDetailsModelSerializer(CustomBaseModelSerializer):

    class Meta:
        model = ShopDetailsModel
        fields = "__all__"


class ShopPermissionsModelSerializer(CustomBaseModelSerializer):
    shop = ShopDetailsModelSerializer(read_only=True)
    class Meta:
        model = ShopPermissionsModel
        fields = "__all__"