

from customCalsses.BaseFilterSet import BaseFilterSet

from .models import CustomerDetailsModel

class CustomerDetailsModelFilterSet(BaseFilterSet):
    class Meta:
        model = CustomerDetailsModel
        fields = "__all__"