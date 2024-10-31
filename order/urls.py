from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout_selection'),
    path('checkout/add-address/', views.handle_address_creation, name='add_address'),
    path('checkout/payment/', views.handle_stripe_payment, name='stripe_payment'), 
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),

    path('my_order/',views.my_order,name='my_order'),
]
