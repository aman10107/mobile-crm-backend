from django.urls import path, include
from .views import CustomerDetailsModelViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', CustomerDetailsModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
