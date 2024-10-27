from django.db import models
from django.conf import settings
from main.models import Cart

class Addresss(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.address_line}, {self.city}, {self.state}, {self.country}"


class Orders(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    address= models.ForeignKey(Addresss, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Non-nullable
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    ORDER_STATUS = (
        (1, "Pending"),
        (2, "Dispatched"),
        (3, "On the way"),
        (4, "Delivered"),
        (5, "Cancelled"), 
        (6, "Returned")
    )
    status = models.IntegerField(choices=ORDER_STATUS, default=1) 
    is_paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    PAYMENT_METHOD_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('STRIPE', 'Stripe')
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    def __str__(self):
        return f"Order {self.id} for {self.cart.user.email}"


class Payments(models.Model):
    order = models.OneToOneField(Orders, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return f"Payment {self.payment_id or 'N/A'} for Order {self.order.id}"

        
