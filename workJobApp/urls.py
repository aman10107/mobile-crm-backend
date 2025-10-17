from django.urls import path, include
from .views import JobDetailsModelViewSet, JobAuditLogView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', JobDetailsModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('jobs/<int:job_id>/audit-logs/', JobAuditLogView.as_view(), name='job-audit-logs')
]
