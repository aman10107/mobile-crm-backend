# paymentApp/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from customerApp.models import CustomerDetailsModel
from customCalsses.BaseModel import BaseModel
from rest_framework.response import Response
from rest_framework import status
class PaymentRecordDetailsModel(BaseModel):
    """Simple payment record"""
    customer = models.ForeignKey(
        CustomerDetailsModel, 
        on_delete=models.CASCADE,
        related_name='payment_records'
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.customer} - ₹{self.amount}"


class CustomerBalanceModel(BaseModel):
    """Cached customer balance - updated automatically"""
    customer = models.OneToOneField(
        CustomerDetailsModel,
        on_delete=models.CASCADE,
        related_name='balance',
        primary_key=True
    )
    balane_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    last_payment_date = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer} - Balance: ₹{self.total_paid}"
    
    def recalculate(self):
        """Recalculate balance from all payments"""
        from workJobApp.models import JobDetailsModel
        result = PaymentRecordDetailsModel.objects.filter(
            customer=self.customer
        ).aggregate(
            total=models.Sum('amount'),
            last_date=models.Max('payment_date')
        )
        jobs_total = JobDetailsModel.objects.filter(
            customer = self.customer,
            status = JobDetailsModel.STATUS_CHOICES.DELIVERED
        ).aggregate(
            total = models.Sum('final_bill')
        )
        total_remainaing = jobs_total['total'] or Decimal('0.00')
        total_paid = result['total'] or Decimal('0.00')
        self.balane_amount = total_paid - total_remainaing
        self.total_paid = total_paid
        self.last_payment_date = result['last_date']
        self.save()
