# your_app/templatetags/custom_tags.py

from django import template
from main.models import Product

register = template.Library()

@register.filter
def applydiscount(product):
    if not product:
        return "no discount"
    
    try:
        price = float(product.price)
        discount = float(product.discount) if product.discount else 0
        final_price = price - discount
        return round(final_price, 2)
    
    except ValueError:
        return "invalid price"
