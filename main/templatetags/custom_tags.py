# your_app/templatetags/custom_tags.py

from django import template
from main.models import Product  # Ensure this import is correct

register = template.Library()

@register.filter
def applydiscount(product_id):
    try:
        product = Product.objects.get(id=product_id)
        discount_percentage = 0.10  # Example: 10% discount
        
        # Ensure that product.price is converted to a float
        original_price = float(product.price)  # Convert to float
        discounted_price = original_price * (1 - discount_percentage)

        return round(discounted_price, 2)  # Return the discounted price rounded to 2 decimal places
    except Product.DoesNotExist:
        return 'no discount'  # Handle case where product does not exist
    except ValueError:
        return "no dicount"  # Handle case where price conversion fails
