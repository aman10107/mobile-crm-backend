

from customCalsses.BaseFilterSet import BaseFilterSet

from .models import EmployeeDetailsModel, EmployeeAttendanceDetailsModel


class EmployeeDetailsModelFilterSet(BaseFilterSet):
    # Accepts single value or comma-separated values:
    # status = CharInFilter(field_name="status", lookup_expr="in")
    class Meta:
        model = EmployeeDetailsModel
        fields = "__all__"

class EmployeeAttendanceDetailsModelFilterSet(BaseFilterSet):
    # Accepts single value or comma-separated values:
    # status = CharInFilter(field_name="status", lookup_expr="in")
    class Meta:
        model = EmployeeAttendanceDetailsModel
        fields = "__all__"