# custom_filters.py

from django import template

register = template.Library()

@register.filter
def format_days(days_list):
    if not days_list:
        return ""
    if len(days_list) == 1:
        return days_list[0]
    return ", ".join(days_list[:-1]) + ", and " + days_list[-1]
