from django.urls import path
from . import views 

urlpatterns = [
    path('user_login/', views.user_login, name='user_login'),
    path('user_register/', views.user_register, name='user_register'),
    path('user_logout/', views.user_logout, name='user_logout'),
   
    path('verify/', views.verify, name='verify'), 
    path('forgetpassword/', views.forgetpassword, name='forgetpassword'),
    path('reset/<uidb64>/<token>/', views.newpassword, name='newpassword'), 

    path('change-password/', views.change_password, name="change_password"),
    path('profile/',views.profile, name="profile"),

    path('wallet/',views.wallet,name='wallet'),
]