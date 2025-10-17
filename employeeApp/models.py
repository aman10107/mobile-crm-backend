from django.db import models

# Create your models here.
from django.contrib.auth.models import  User
from customCalsses.BaseModel import BaseModel
from django.utils import timezone

class EmployeeDetailsModel(BaseModel):
    class JOB_PROFILE_CHOICES(models.TextChoices):
        TECHNICIAN = 'technician', 'Technician'

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=300)
    last_name = models.CharField(max_length=300)
    job_profile = models.CharField(max_length=200, choices=JOB_PROFILE_CHOICES.choices)

    def save(self, *args, **kwargs):
        # If user is not set but email is provided, try to find user by email
        if not self.user and self.email:
            try:
                user = User.objects.get(email=self.email)
                self.user = user
            except User.DoesNotExist:
                # User with this email doesn't exist, keep user as None
                pass
            except User.MultipleObjectsReturned:
                # Multiple users with same email, keep user as None for safety
                pass
        
        # If user is set but email is not provided, get email from user
        elif self.user and not self.email:
            self.email = self.user.email
        
        # If both user and email are provided, update email from user
        elif self.user and self.email:
            # Optionally sync email from user (uncomment if you want this behavior)
            self.email = self.user.email
            pass
        
        # Call the original save method
        super().save(*args, **kwargs)




class EmployeeAttendanceDetailsModel(BaseModel):
    class ATTENDANCE_STATUS(models.TextChoices):
        PRESENT = 'Present', 'Present'
        ABSENT = 'Absent', 'Absent'
        HALF_DAY = 'Half Day', 'Half Day'
        # LATE = 'Late', 'Late'
    
    employee = models.ForeignKey(EmployeeDetailsModel, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS.choices)
    notes = models.TextField(blank=True, help_text="Any additional notes about attendance")
    marked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'date']  # One attendance record per employee per day
        ordering = ['-date', 'employee__first_name']
    
    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} - {self.date} ({self.status})"