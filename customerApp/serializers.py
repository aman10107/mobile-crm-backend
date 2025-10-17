from  customCalsses.CustomBaseModelSerializer import CustomBaseModelSerializer
from .models import CustomerDetailsModel


class CustomerDetailsModelSerializer(CustomBaseModelSerializer):
    class Meta:
        model = CustomerDetailsModel
        fields = "__all__"

