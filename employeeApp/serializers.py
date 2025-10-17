from  customCalsses.CustomBaseModelSerializer import CustomBaseModelSerializer
from .models import EmployeeDetailsModel, EmployeeAttendanceDetailsModel

class EmployeeDetailsModelSerializer(CustomBaseModelSerializer):
    class Meta:
        model = EmployeeDetailsModel
        fields = "__all__"


from rest_framework import serializers

class EmployeeAttendanceDetailsModelSerializer(CustomBaseModelSerializer):
    employee_name = serializers.CharField(source='employee.first_name', read_only=True)
    employee_last_name = serializers.CharField(source='employee.last_name', read_only=True)
    employee_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeeAttendanceDetailsModel
        fields = '__all__'
        read_only_fields = ['marked_by', 'created_at', 'updated_at']
    
    def get_employee_full_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    
    def create(self, validated_data):
        # Automatically set the marked_by field to current user
        validated_data['marked_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Update marked_by when attendance is modified
        validated_data['marked_by'] = self.context['request'].user
        return super().update(instance, validated_data)


# class BulkAttendanceSerializer(serializers.Serializer):
#     """Serializer for marking attendance for multiple employees at once"""
#     date = serializers.DateField()
#     attendances = serializers.ListField(
#         child=serializers.DictField(
#             child=serializers.CharField()
#         )
#     )
#     # Expected format: 
#     # {
#     #   "date": "2025-10-16",
#     #   "attendances": [
#     #     {"employee_id": "1", "status": "Present", "notes": ""},
#     #     {"employee_id": "2", "status": "Absent", "notes": "Sick leave"}
#     #   ]
#     # }
