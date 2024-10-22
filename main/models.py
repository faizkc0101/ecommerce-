from django.db import models

# Create your models here.

class Carousel(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.FileField(null=True, blank=True)
    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.CharField(max_length=100, null=True, blank=True)
    discount = models.CharField(max_length=100, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



#cart setup
from django.conf import settings

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.email}"

    @property
    def total_price(self):
        # Calculate the total 
        total = sum(item.subtotal() for item in self.cartitem_set.all())
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    def subtotal(self):
        return self.quantity * float(self.product.price)



ORDER_STATUS = (
    (1, "Pending"),
    (2, "Dispatched"),
    (3, "On the way"),
    (4, "Delivered"),
    (5, "Cancelled"),
    (6, "Returned")
)


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(CartItem)  # Link CartItems to the booking
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField(choices=ORDER_STATUS, default=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking by {self.user.email}"


