from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout_selection'),
    path('checkout/add-address/', views.handle_address_creation, name='add_address'),
    path('checkout/payment/', views.handle_stripe_payment, name='stripe_payment'), 
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),

    path('my_order/',views.my_order,name='my_order'),
    path('user_order_track/<int:order_id>/',views.user_order_track,name='user_order_track'),
    path('change-order-status/<int:pid>/', views.change_order_status, name="change_order_status"),

    path('order/<int:order_id>/request-return/', views.request_return, name='request_return'),
]
