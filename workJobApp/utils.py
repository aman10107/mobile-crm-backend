from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
import json

def get_field_verbose_name(model_class, field_name):
    """Get the verbose name of a model field"""
    try:
        field = model_class._meta.get_field(field_name)
        return field.verbose_name.title()
    except:
        return field_name.replace('_', ' ').title()

def format_field_value(field_name, value, model_class):
    """Format field value for display"""
    if value is None:
        return "Empty"
    
    # Handle foreign keys
    if field_name in ['shop', 'customer']:
        return str(value)
    
    # Handle choice fields
    try:
        field = model_class._meta.get_field(field_name)
        if hasattr(field, 'choices') and field.choices:
            # Convert the value to its display form
            choices_dict = dict(field.choices)
            return choices_dict.get(value, value)
    except:
        pass
    
    return str(value)

def generate_audit_message(log_entry, model_class):
    """Generate human-readable message from log entry"""
    action = log_entry.action
    user = log_entry.actor.username if log_entry.actor else "System"
    timestamp = log_entry.timestamp.strftime("%B %d, %Y at %I:%M %p")
    
    if action == 0:  # Create
        # return f"{user} created this job on {timestamp}"
        return f"{user} created this job."
    
    elif action == 1:  # Update
        # FIX: Handle both dict and string formats
        if isinstance(log_entry.changes, str):
            changes = json.loads(log_entry.changes)
        elif isinstance(log_entry.changes, dict):
            changes = log_entry.changes
        else:
            changes = {}
        
        if not changes:
            # return f"{user} updated this job on {timestamp}"
            return f"{user} updated this job."
        
        
        # Build detailed message
        change_messages = []
        for field_name, (old_value, new_value) in changes.items():
            field_label = get_field_verbose_name(model_class, field_name)
            old_display = format_field_value(field_name, old_value, model_class)
            new_display = format_field_value(field_name, new_value, model_class)
            
            change_messages.append(
                f"changed {field_label} from '{old_display}' to '{new_display}'"
            )
        
        if len(change_messages) == 1:
            # return f"{user} {change_messages[0]} on {timestamp}"
            return f"{user} {change_messages[0]}."
        elif len(change_messages) == 2:
            # return f"{user} {change_messages[0]} and {change_messages[1]} on {timestamp}"
            return f"{user} {change_messages[0]} and {change_messages[1]}."
        else:
            # Multiple changes
            all_but_last = ", ".join(change_messages[:-1])
            # return f"{user} {all_but_last}, and {change_messages[-1]} on {timestamp}"
            return f"{user} {all_but_last}, and {change_messages[-1]}."
    
    elif action == 2:  # Delete
        # return f"{user} deleted this job on {timestamp}"
        return f"{user} deleted this job."
    
    # return f"{user} performed an action on {timestamp}"
    return f"{user} performed an action."



from auditlog.context import set_actor

class AuditLogMixin:
    """Mixin to automatically set the actor for auditlog in DRF views"""
    
    def dispatch(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            with set_actor(request.user):
                return super().dispatch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)