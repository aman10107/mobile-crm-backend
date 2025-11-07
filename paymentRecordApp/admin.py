from django.contrib import admin

# Register your models here.

from .models import PaymentRecordDetailsModel, CustomerBalanceModel

admin.site.register(PaymentRecordDetailsModel)
admin.site.register(CustomerBalanceModel)