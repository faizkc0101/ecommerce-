
from django.urls import path
from main import views

  
urlpatterns = [
    path('home', views.home, name="home"),
    path('index', views.index, name="index"),
    path('about/', views.about, name="about"),
    path('',views.main, name="main"),
    path('user-product/<int:pid>/', views.user_product, name="user_product"),
    path('product-detail/<int:pid>/', views.product_detail, name="product_detail"),

    path('add-to-cart/<int:pid>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('update-cart-item/<int:pid>/<str:action>/', views.update_cart_item, name='update_cart_item'),
    path('remove-cart-item/<int:pid>/', views.remove_cart_item, name='remove_cart_item'),
    
    path('booking/',views.booking, name= 'booking'),
    path('my-order/', views.myOrder, name="myorder"),
    path('user-order-track/<int:pid>/', views.user_order_track, name="user_order_track"),
    path('change-order-status/<int:pid>/', views.change_order_status, name="change_order_status"),
    

]
