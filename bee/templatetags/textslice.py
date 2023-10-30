from django import template

register = template.Library()

@register.filter
def remove_rewrite(value):
    if value==None: return value
    if "[Written by MAL Rewrite]" in value:
        return value.replace("[Written by MAL Rewrite]", "")
    else: return value