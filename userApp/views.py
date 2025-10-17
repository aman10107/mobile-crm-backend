from django.shortcuts import render

# Create your views here.

from customCalsses.CustomBaseModelViewSet import CustomBaseModelViewSet
from .models import UserDetailsModel
from .serializers import UserDetailsSerializer
from helpers.PaginationClass import CustomPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .filters import UserDetailsModelFilterSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action


class UserDetailsModelViewSet(CustomBaseModelViewSet):
    queryset = UserDetailsModel.objects.all()
    serializer_class = UserDetailsSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserDetailsModelFilterSet
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        # only return objects belonging to the logged-in user
        return UserDetailsModel.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.get(user=request.user.id)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)
        