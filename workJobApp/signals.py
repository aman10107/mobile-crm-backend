# paymentApp/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import JobDetailsModel
from paymentRecordApp.models import CustomerBalanceModel


@receiver(post_save, sender=JobDetailsModel)
def update_balance_on_payment_save(sender, instance, created, **kwargs):
    """Update customer balance when payment is added or updated"""
    balance, created = CustomerBalanceModel.objects.get_or_create(
        shop = instance.shop,
        customer=instance.customer
    )
    balance.recalculate()


@receiver(post_delete, sender=JobDetailsModel)
def update_balance_on_payment_delete(sender, instance, **kwargs):
    """Update customer balance when payment is deleted"""
    try:
        balance = CustomerBalanceModel.objects.get(customer=instance.customer)
        balance.recalculate()
    except CustomerBalanceModel.DoesNotExist:
        pass
