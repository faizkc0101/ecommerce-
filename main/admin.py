from django.contrib import admin
from main.models import *

admin.site.register(Carousel)

admin.site.register(Category)
admin.site.register(Product)

admin.site.register(Cart)
admin.site.register(CartItem)

admin.site.register(Wishlist)