from django_filters import rest_framework as filters
from django.db.models import (
    ForeignKey, ManyToManyField, ImageField, FileField,
    DateField, DateTimeField, CharField, TextField
)
from functools import partial

class BaseFilterSet(filters.FilterSet):
    """Enhanced BaseFilterSet with:
    - Multi-value filtering for ForeignKey, ManyToMany, Char/Text fields
    - Partial search (__contains) for Char/Text fields
    - Date lookups: exact, lt, lte, gt, gte, range
    - No-op for Image/File fields
    """

    @classmethod
    def filter_for_field(cls, f, name, lookup_expr=None):
        if isinstance(f, (ImageField, FileField)):
            # No-op filter
            return filters.CharFilter(method=lambda qs, name, value: qs)

        # Date fields handled in __init__
        if isinstance(f, (DateField, DateTimeField)):
            return None

        # Char/Text fields handled in __init__ for multi-value & contains
        if isinstance(f, (CharField, TextField)):
            return None

        return super().filter_for_field(f, name, lookup_expr)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = self.Meta.model

        for field in model._meta.get_fields():
            field_name = field.name

            # Multi-value support for ForeignKey and ManyToMany
            if isinstance(field, (ForeignKey, ManyToManyField)):
                self.filters[field_name] = filters.CharFilter(
                    method=partial(self.filter_multiple_values, field_name)
                )

            # Multi-value + partial search for Char/Text fields
            elif isinstance(field, (CharField, TextField)):
                # multi-value __in
                self.filters[field_name] = filters.CharFilter(
                    method=partial(self.filter_multiple_values, field_name)
                )
                # partial search __contains
                self.filters[f"{field_name}__contains"] = filters.CharFilter(
                    field_name=field_name, lookup_expr="icontains"
                )

            # Date filters automatically
            elif isinstance(field, (DateField, DateTimeField)):
                self.filters[f"{field_name}"] = filters.DateFilter(field_name=field_name, lookup_expr="exact")
                self.filters[f"{field_name}__lt"] = filters.DateFilter(field_name=field_name, lookup_expr="lt")
                self.filters[f"{field_name}__lte"] = filters.DateFilter(field_name=field_name, lookup_expr="lte")
                self.filters[f"{field_name}__gt"] = filters.DateFilter(field_name=field_name, lookup_expr="gt")
                self.filters[f"{field_name}__gte"] = filters.DateFilter(field_name=field_name, lookup_expr="gte")
                self.filters[f"{field_name}__range"] = filters.DateFromToRangeFilter(field_name=field_name)

    def filter_multiple_values(self, field_name, queryset, name, value):
        """Split comma-separated values and apply __in filter."""
        values = value.split(",")
        return queryset.filter(**{f"{field_name}__in": values})




# | Query parameter        | Meaning               |
# | ---------------------- | --------------------- |
# | `reminder_date`        | exact match           |
# | `reminder_date__lt`    | less than             |
# | `reminder_date__lte`   | less than or equal    |
# | `reminder_date__gt`    | greater than          |
# | `reminder_date__gte`   | greater than or equal |
# | `reminder_date__range` | between two dates     |
