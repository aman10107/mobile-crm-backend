from django.contrib import admin

# Register your models here.
from .models import ShopDetailsModel, ShopPermissionsModel

admin.site.register(ShopDetailsModel)
admin.site.register(ShopPermissionsModel)