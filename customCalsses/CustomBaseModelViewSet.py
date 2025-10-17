
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from auditlog.context import set_actor


class ShopMixin:
    """
    Mixin to automatically populate shop field from query parameters
    """
    def perform_create(self, serializer):
        # Check if model has a 'shop' field
        model = serializer.Meta.model
        if hasattr(model, 'shop'):
            shop_id = self.request.query_params.get('shop')
            print(f"DEBUG: Auto-populating shop_id = {shop_id}")  # Debug
            if shop_id:
                serializer.save(shop_id=shop_id)
            else:
                # If no shop_id in params, just save normally
                serializer.save()
        else:
            serializer.save()


class AuditLogMixin:
    """
    Mixin to automatically set the actor for auditlog in DRF views
    """
    def perform_create(self, serializer):
        """Override perform_create to set actor for audit logging"""
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            with set_actor(self.request.user):
                super().perform_create(serializer)
        else:
            super().perform_create(serializer)
    
    def perform_update(self, serializer):
        """Override perform_update to set actor for audit logging"""
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            with set_actor(self.request.user):
                super().perform_update(serializer)
        else:
            super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        """Override perform_destroy to set actor for audit logging"""
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            with set_actor(self.request.user):
                super().perform_destroy(instance)
        else:
            super().perform_destroy(instance)


class CustomBaseModelViewSet_ChoicesMixin:
    @action(detail=False, methods=['get'], url_path='choices', url_name='choices')
    def choices(self, request, *args, **kwargs):
        model = self.queryset.model
        choices = {}
        
        # Iterate over all fields in the model
        for field in model._meta.fields:
            if field.choices:
                # Add the field name and its choices to the response
                choices[field.name + "_choices"] = [{'key': key, 'value': value} for key, value in field.choices]
        
        return Response(choices)
    
    
    def retrieve(self, request, *args, **kwargs):
        # Call the original retrieve method
        response = super().retrieve(request, *args, **kwargs)
        
        # Check if the 'model_choices' query parameter is present and true
        include_choices = request.query_params.get('get_model_choices', 'false').lower() == 'true'
        
        if include_choices:
            # Get the model from the queryset
            model = self.queryset.model
            
            # Dynamically add choices fields to the response
            choices = {}
            for field in model._meta.fields:
                if field.choices:
                    choices[field.name + "_choices"] = [
                        {"key": key, "value": value} for key, value in field.choices
                    ]
            
            # Update the response data with choices
            response.data.update(choices)
        
        return response


class CustomBaseModelViewSet(AuditLogMixin, ShopMixin, CustomBaseModelViewSet_ChoicesMixin, ModelViewSet):
    """
    Custom base viewset with:
    - Automatic auditlog actor tracking
    - Automatic shop field population from query params
    - Model choices retrieval endpoint
    - Model choices in retrieve response
    
    Usage:
        class YourViewSet(CustomBaseModelViewSet):
            queryset = YourModel.objects.all()
            serializer_class = YourSerializer
    """
    pass


# class ChoicesMixin:
#     @action(detail=False, methods=['get'], url_path='choices', url_name='choices')
#     def choices(self, request, *args, **kwargs):
#         model = self.queryset.model
#         choices = {}
        
#         # Iterate over all fields in the model
#         for field in model._meta.fields:
#             if field.choices:
#                 # If the field has choices, check if they include a color
#                 field_choices = []
#                 for choice in model.STATUS_CHOICES:
#                     if len(choice) == 3:  # Includes color
#                         field_choices.append({
#                             'key': choice[0],
#                             'label': choice[1],
#                             'color': choice[2]
#                         })
#                     else:
#                         field_choices.append({
#                             'key': choice[0],
#                             'label': choice[1],
#                         })
#                 choices[field.name] = field_choices
        
#         return Response(choices)
