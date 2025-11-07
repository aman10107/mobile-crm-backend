from  customCalsses.CustomBaseModelSerializer import CustomBaseModelSerializer
from .models import PaymentRecordDetailsModel, CustomerBalanceModel


class PaymentRecordDetailsModelSerializer(CustomBaseModelSerializer):
    class Meta:
        model = PaymentRecordDetailsModel
        fields = "__all__"

class CustomerBalanceModelSerializer(CustomBaseModelSerializer):
    class Meta:
        model = CustomerBalanceModel
        fields = "__all__"

