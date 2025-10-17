

from customCalsses.BaseFilterSet import BaseFilterSet

from .models import JobDetailsModel
from django_filters import rest_framework as filters

# Helper: django-filter provides BaseInFilter to accept comma-separated lists
class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass

class JobDetailsModelFilterSet(BaseFilterSet):
    # Accepts single value or comma-separated values:
    # status = CharInFilter(field_name="status", lookup_expr="in")
    class Meta:
        model = JobDetailsModel
        fields = "__all__"