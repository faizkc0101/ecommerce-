from django.urls import path
from main import views

urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
   
    path('user-product/<int:pid>/', views.user_product, name="user_product"),
    path('product-detail/<int:pid>/', views.product_detail, name="product_detail"),

    path('add-to-cart/<int:pid>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('update-cart-item/<int:pid>/<str:action>/', views.update_cart_item, name='update_cart_item'),
    path('remove-cart-item/<int:pid>/', views.remove_cart_item, name='remove_cart_item'),
    
    path('search/',views.search,name='search'),

    path('wishlist/',views.wishlist,name='wishlist'),
    path('add_wishlist/<int:pid>/',views.add_to_wishlist,name='add_wishlist'),
    path('remove_from_wishlist/<int:pid>/',views.remove_from_wishlist,name='remove_from_wishlist'),

]
