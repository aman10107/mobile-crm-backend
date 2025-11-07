

from customCalsses.BaseFilterSet import BaseFilterSet

from .models import PaymentRecordDetailsModel, CustomerBalanceModel

class PaymentRecordDetailsModelFilterSet(BaseFilterSet):
    class Meta:
        model = PaymentRecordDetailsModel
        fields = "__all__"

class CustomerBalanceModelFilterSet(BaseFilterSet):
    class Meta:
        model = CustomerBalanceModel
        fields = "__all__"