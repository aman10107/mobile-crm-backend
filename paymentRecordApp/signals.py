# paymentApp/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PaymentRecordDetailsModel, CustomerBalanceModel, PaymentAllocationModel


@receiver(post_save, sender=PaymentRecordDetailsModel)
def update_balance_on_payment_save(sender, instance, created, **kwargs):
    """Update customer balance when payment is added or updated"""
    balance, created = CustomerBalanceModel.objects.get_or_create(
        shop = instance.shop,
        customer=instance.customer
    )
    balance.recalculate()


@receiver(post_delete, sender=PaymentRecordDetailsModel)
def update_balance_on_payment_delete(sender, instance, **kwargs):
    """Update customer balance when payment is deleted"""
    try:
        balance = CustomerBalanceModel.objects.get(customer=instance.customer)
        balance.recalculate()
    except CustomerBalanceModel.DoesNotExist:
        pass


@receiver(post_save, sender=PaymentAllocationModel)
def update_job_payment_status_on_allocation_save(sender, instance, **kwargs):
    """Keep the job's amount_paid/payment_status in sync with its allocations"""
    instance.job.recalculate_payment_status()


@receiver(post_delete, sender=PaymentAllocationModel)
def update_job_payment_status_on_allocation_delete(sender, instance, **kwargs):
    """Keep the job's amount_paid/payment_status in sync after an allocation is removed"""
    instance.job.recalculate_payment_status()
