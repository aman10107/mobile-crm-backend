from django.urls import path, include
from .views import UserDetailsModelViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'details', UserDetailsModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
