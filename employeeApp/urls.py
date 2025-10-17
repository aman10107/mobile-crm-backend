from django.urls import path, include
from .views import EmployeeDetailsModelViewSet, EmployeeAttendanceDetailsModelViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'employees', EmployeeDetailsModelViewSet)
router.register(r'attendance', EmployeeAttendanceDetailsModelViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
