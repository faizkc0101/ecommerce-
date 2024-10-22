from django.urls import path
from myadmin import views

urlpatterns = [
    path('admin-login/',views.adminLogin, name="admin_login"),
    path('admindashboard/',views.admin_dashboard, name="admindashboard"),
    path('add-category/', views.add_category, name="add_category"),
    path('view-category/',views.view_category, name="view_category"),
    path('edit-category/<int:pid>/', views.edit_category, name="edit_category"),
    path('delete-category/<int:pid>/', views.delete_category, name="delete_category"),
    
    path('add-product/', views.add_product, name='add_product'),
    path('view-product/',views.view_product, name='view_product'),
    path('edit-product/<int:pid>/', views.edit_product, name="edit_product"),
    path('delete-product/<int:pid>/', views.delete_product, name="delete_product"),
]
