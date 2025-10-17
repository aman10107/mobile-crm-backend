from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.

from customCalsses.CustomBaseModelViewSet import CustomBaseModelViewSet
from .models import CustomerDetailsModel
from .serializers import CustomerDetailsModelSerializer
from helpers.PaginationClass import CustomPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import CustomerDetailsModelFilterSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters as drf_filters

class CustomerDetailsModelViewSet(CustomBaseModelViewSet):
    queryset = CustomerDetailsModel.objects.all()
    serializer_class = CustomerDetailsModelSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_class = CustomerDetailsModelFilterSet
    permission_classes = [IsAuthenticated]
    search_fields = ['first_name', 'last_name', 'phone_number']  # fields to search 