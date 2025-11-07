from django.urls import path, include
from .views import PaymentRecordDetailsModelViewSet, CustomerBalanceModelModelViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'customers_balance', CustomerBalanceModelModelViewSet)
router.register(r'', PaymentRecordDetailsModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
