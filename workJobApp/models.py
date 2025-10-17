from django.db import models
from customerApp.models import CustomerDetailsModel
from shopApp.models import ShopDetailsModel
from auditlog.registry import auditlog
from employeeApp.models import EmployeeDetailsModel
from django.core.exceptions import ValidationError

def validate_technician(value):
    # """Validate that the assigned technician has TECHNICIAN job profile"""
    # if value:
    #     try:
    #         employee = value.technician  # Adjust based on your relationship
    #         if employee.job_profile != EmployeeDetailsModel.JOB_PROFILE_CHOICES.TECHNICIAN:
    #             raise ValidationError('Only employees with Technician job profile can be assigned.')
    #     except Exception as e:
    #         print()
    #         raise ValidationError('Invalid technician selection.', Exception)
    pass
        
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class JobDetailsModel(models.Model):
    class STATUS_CHOICES(models.TextChoices):
        ASSIGNED = 'assigned', 'Assigned'
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        DELIVERED = "delivered", "Delivered"
    
    # Your existing fields
    shop = models.ForeignKey(ShopDetailsModel, on_delete=models.CASCADE, verbose_name="Shop")
    reminder_date = models.DateField(verbose_name="Reminder Date")
    customer = models.ForeignKey(CustomerDetailsModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Customer")
    job_no = models.CharField(max_length=40, verbose_name="Job Number")
    model = models.CharField(max_length=256, verbose_name="Model")
    job_details = models.CharField(max_length=1000, verbose_name="Job Details")
    technician = models.ForeignKey(EmployeeDetailsModel, on_delete=models.SET_NULL, null=True, validators=[validate_technician])
    note = models.TextField(null=True, blank=True, verbose_name="Notes")
    status = models.CharField(max_length=40, choices=STATUS_CHOICES.choices, verbose_name="Status")
    delivery = models.DateField(verbose_name="Delivery Date")
    feedback = models.TextField(null=True, blank=True, verbose_name="Customer Feedback")
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Cost")
    estimated_bill = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Estimated Bill")
    final_bill = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Final Bill")
    
    # PERFORMANCE ANALYTICS FIELDS
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At", db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Work Started At")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Work Completed At")
    
    # Time tracking for performance
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Estimated Hours")
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Actual Hours Worked")
    
    # Performance indicators
    first_time_fix = models.BooleanField(default=True, verbose_name="First Time Fix")
    rework_required = models.BooleanField(default=False, verbose_name="Rework Required")
    
    # FINANCIAL ANALYTICS FIELDS
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Parts Cost")
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Labor Cost")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Discount Amount")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Tax Amount")
    
    # COMPUTED PROPERTIES FOR ANALYTICS
    @property
    def total_cost(self):
        """Calculate total cost including parts and labor"""
        parts = self.parts_cost or 0
        labor = self.labor_cost or 0
        return parts + labor if (parts + labor) > 0 else None
    
    @property
    def profit_amount(self):
        """Calculate profit amount"""
        if self.final_bill and self.total_cost:
            return self.final_bill - self.total_cost
        return None
    
    @property
    def profit_margin_percentage(self):
        """Calculate profit margin percentage"""
        if self.final_bill and self.total_cost and self.final_bill > 0:
            return ((self.final_bill - self.total_cost) / self.final_bill) * 100
        return None
    
    @property
    def hours_efficiency_percentage(self):
        """Calculate efficiency: estimated vs actual hours"""
        if self.estimated_hours and self.actual_hours and self.actual_hours > 0:
            return (self.estimated_hours / self.actual_hours) * 100
        return None
    
    @property
    def completion_time_days(self):
        """Days taken to complete the job"""
        if self.completed_at and self.started_at:
            return (self.completed_at.date() - self.started_at.date()).days
        return None
    
    @property
    def is_overdue(self):
        """Check if job is overdue"""
        return (self.delivery < timezone.now().date() and 
                self.status not in ['completed', 'delivered'])
    
    @property
    def revenue_per_hour(self):
        """Calculate revenue per hour worked"""
        if self.final_bill and self.actual_hours and self.actual_hours > 0:
            return self.final_bill / self.actual_hours
        return None

    class Meta:
        verbose_name = "Job Detail"
        verbose_name_plural = "Job Details"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['technician', 'completed_at']),
            models.Index(fields=['shop', 'delivery']),
            models.Index(fields=['final_bill', 'completed_at']),
        ]



auditlog.register(JobDetailsModel)


