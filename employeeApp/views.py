from django.shortcuts import render

# Create your views here.

from customCalsses.CustomBaseModelViewSet import CustomBaseModelViewSet
from .models import EmployeeDetailsModel, EmployeeAttendanceDetailsModel
from .serializers import EmployeeDetailsModelSerializer, EmployeeAttendanceDetailsModelSerializer
from helpers.PaginationClass import CustomPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .filters import EmployeeDetailsModelFilterSet, EmployeeAttendanceDetailsModelFilterSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters


class EmployeeDetailsModelViewSet(CustomBaseModelViewSet):
    queryset = EmployeeDetailsModel.objects.all()
    serializer_class = EmployeeDetailsModelSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = EmployeeDetailsModelFilterSet
    permission_classes = [IsAuthenticated] 
    ordering_fields = '__all__'
    search_fields = ['first_name', 'last_name', 'email', 'job_profile']

    
class EmployeeAttendanceDetailsModelViewSet(CustomBaseModelViewSet):
    queryset = EmployeeAttendanceDetailsModel.objects.all()
    serializer_class = EmployeeAttendanceDetailsModelSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = EmployeeAttendanceDetailsModelFilterSet
    permission_classes = [IsAuthenticated] 
    ordering_fields = '__all__'
    # search_fields = ['first_name', 'last_name', 'email', 'job_profile']