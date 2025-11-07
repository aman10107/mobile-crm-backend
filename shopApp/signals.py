
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ShopDetailsModel, ShopPermissionsModel

@receiver(post_save, sender=ShopDetailsModel)
def create_or_update_shop_permission(sender, instance, created, **kwargs):
    permission, _ = ShopPermissionsModel.objects.get_or_create(
        shop=instance,
        defaults={'email': instance.owner.email}
    )
    
    if not created and permission.email != instance.owner.email:
        permission.email = instance.owner.email
        permission.save()