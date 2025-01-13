from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Filtro para obtener un valor de un diccionario por clave"""
    return dictionary.get(key)