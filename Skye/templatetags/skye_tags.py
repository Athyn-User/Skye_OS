from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    '''Get item from dictionary using key'''
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter  
def slugify(value):
    '''Convert to URL-friendly slug'''
    return value.lower().replace(' ', '-').replace('_', '-')