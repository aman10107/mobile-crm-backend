from  customCalsses.CustomBaseModelSerializer import CustomBaseModelSerializer
from .models import JobDetailsModel

from rest_framework import serializers
from auditlog.models import LogEntry

class JobDetailsModelSerializer(CustomBaseModelSerializer):
    amount_remaining = serializers.SerializerMethodField()

    class Meta:
        model = JobDetailsModel
        fields = "__all__"
        extra_kwargs = {
            'job_no': {'required': False},
            'amount_paid': {'read_only': True},
            'payment_status': {'read_only': True},
        }

    def get_amount_remaining(self, obj):
        return obj.amount_remaining



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
