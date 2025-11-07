from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.

from customCalsses.CustomBaseModelViewSet import CustomBaseModelViewSet
from .models import PaymentRecordDetailsModel, CustomerBalanceModel
from .serializers import PaymentRecordDetailsModelSerializer, CustomerBalanceModelSerializer
from helpers.PaginationClass import CustomPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import PaymentRecordDetailsModelFilterSet, CustomerBalanceModelFilterSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters as drf_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

class PaymentRecordDetailsModelViewSet(CustomBaseModelViewSet):
    queryset = PaymentRecordDetailsModel.objects.all()
    serializer_class = PaymentRecordDetailsModelSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter, drf_filters.SearchFilter]
    filterset_class = PaymentRecordDetailsModelFilterSet
    permission_classes = [IsAuthenticated]
    ordering_fields = '__all__'
    search_fields = ['customer__first_name', 'customer__last_name'] 

    @action(detail=False, methods=['get'], url_path='shop_balance')
    def shopBalanceDetails(self, request):
        from .utils import get_shop_balance
        shop_id = request.query_params.get('shop')
        balance = get_shop_balance(shop_id=shop_id)
        return Response({
            "stats": balance
        }, status=status.HTTP_200_OK)


class CustomerBalanceModelModelViewSet(CustomBaseModelViewSet):
    queryset = CustomerBalanceModel.objects.all()
    serializer_class = CustomerBalanceModelSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter, drf_filters.SearchFilter]
    filterset_class = CustomerBalanceModelFilterSet
    permission_classes = [IsAuthenticated]
    ordering_fields = '__all__'
    search_fields = ['customer__first_name', 'customer__last_name']  # fields to search 

    