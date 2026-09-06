from  customCalsses.CustomBaseModelSerializer import CustomBaseModelSerializer
from .models import JobDetailsModel

from rest_framework import serializers
from auditlog.models import LogEntry

class JobDetailsModelSerializer(CustomBaseModelSerializer):
    class Meta:
        model = JobDetailsModel
        fields = "__all__"



class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()
    changes = serializers.SerializerMethodField()
    
    class Meta:
        model = LogEntry
        fields = ['timestamp', 'user', 'action', 'changes']
    
    def get_user(self, obj):
        return obj.actor.username if obj.actor else 'System'
    
    def get_action(self, obj):
        return obj.get_action_display()
    
    def get_changes(self, obj):
        import json
        return json.loads(obj.changes) if obj.changes else {}
