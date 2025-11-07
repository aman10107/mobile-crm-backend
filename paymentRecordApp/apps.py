# paymentApp/apps.py
from django.apps import AppConfig


class PaymentAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'paymentRecordApp'
    
    def ready(self):
        import paymentRecordApp.signals  # Import signals when app is ready
