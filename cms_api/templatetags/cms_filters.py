from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def split(value, arg):
    """
    Split the value by the argument and return a list.
    Usage: {{ value|split:',' }}
    """
    if value:
        return value.split(arg)
    return []
