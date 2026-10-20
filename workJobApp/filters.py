

from customCalsses.BaseFilterSet import BaseFilterSet

from .models import JobDetailsModel
from django.db.models import Q
from django_filters import rest_framework as filters

# Helper: django-filter provides BaseInFilter to accept comma-separated lists
class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass

class JobDetailsModelFilterSet(BaseFilterSet):
    # Accepts single value or comma-separated values:
    # status = CharInFilter(field_name="status", lookup_expr="in")
    # Partial-match search on related people. Every word must match the first or last name.
    customer_name = filters.CharFilter(method="filter_customer_name")
    customer_phone = filters.CharFilter(field_name="customer__phone_number", lookup_expr="icontains")
    technician_name = filters.CharFilter(method="filter_technician_name")

    @staticmethod
    def _name_filter(qs, prefix, value):
        for term in value.split():
            qs = qs.filter(
                Q(**{f"{prefix}__first_name__icontains": term})
                | Q(**{f"{prefix}__last_name__icontains": term})
            )
        return qs

    def filter_customer_name(self, qs, name, value):
        return self._name_filter(qs, "customer", value)

    def filter_technician_name(self, qs, name, value):
        return self._name_filter(qs, "technician", value)

    class Meta:
        model = JobDetailsModel
        fields = "__all__"