from django.db import models
from django.conf import settings


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
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_discounted_price(self):
        """Calculate the price after applying the discount."""
        if self.discount and self.discount > 0:
            return self.price - self.discount
        return self.price


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.email}"

    @property
    def total_price(self):
        total_discounted = 0
        total_original = 0
        for item in self.cartitem_set.all():
            total_discounted += item.subtotal()  # Discounted subtotal
            total_original += item.subtotal_original()  # Original subtotal
        return {
            'total_discounted': total_discounted,
            'total_original': total_original
        }


class CartItem(models.Model): 
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    def subtotal(self):
        price = float(self.product.price)
        discount = float(self.product.discount) if self.product.discount else 0
        discounted_price = price - discount 
        return round(discounted_price * self.quantity, 2)

    def subtotal_original(self):
        """Calculate the subtotal at original price (without discount)."""
        return round(float(self.product.price) * self.quantity, 2)

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} X {self.product.name}"
    



