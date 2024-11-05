from django.shortcuts import render,redirect, get_object_or_404
from main.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from accounts.models import CustomUser
from order.models import *

def adminLogin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        try:
            if user.is_staff:
                login(request, user)
                messages.success(request,'admin login successfully')
                return redirect('admindashboard')
            else:
                messages.error(request,'Invalid Credentials')
                
        except:
             messages.error(request,'Invalid Credentials')
             
    return render(request, 'myadmin/admin_login.html',locals())
    
import json
from django.shortcuts import render
from django.db.models import Sum, DecimalField
from django.db.models.functions import TruncMonth, Coalesce
from django.db.models import Value
from django.utils.safestring import mark_safe

def admin_dashboard(request):
    # Basic counts
    order_count = Orders.objects.count()
    product_count = Product.objects.count()
    category_count = Category.objects.count()
    user_count = CustomUser.objects.count()

    # Monthly revenue aggregation for COD and Stripe
    revenue_data_cod = list(
        Orders.objects.filter(payment_method='COD')
        .annotate(month=TruncMonth('created'))
        .values('month')
        .annotate(total=Coalesce(Sum('total', output_field=DecimalField()), Value(0, output_field=DecimalField())))
        .order_by('month')
    )

    revenue_data_stripe = list(
        Orders.objects.filter(payment_method='Stripe')
        .annotate(month=TruncMonth('created'))
        .values('month')
        .annotate(total=Coalesce(Sum('total', output_field=DecimalField()), Value(0, output_field=DecimalField())))
        .order_by('month')
    )

    # Overall revenue calculations
    total_revenue_cod = Orders.objects.filter(payment_method='COD').aggregate(total=Coalesce(Sum('total', output_field=DecimalField()), Value(0, output_field=DecimalField())))['total']
    total_revenue_stripe = Orders.objects.filter(payment_method='Stripe').aggregate(total=Coalesce(Sum('total', output_field=DecimalField()), Value(0, output_field=DecimalField())))['total']
    total_revenue = total_revenue_cod + total_revenue_stripe

    context = {
        'order': order_count,
        'product': product_count,
        'category': category_count,
        'customuser': user_count,
        'total_revenue_cod': total_revenue_cod,
        'total_revenue_stripe': total_revenue_stripe,
        'total_revenue': total_revenue,
        'revenue_data_cod': mark_safe(json.dumps(revenue_data_cod, default=str)),
        'revenue_data_stripe': mark_safe(json.dumps(revenue_data_stripe, default=str)),
    }
    return render(request, 'myadmin/admin_dashboard.html', context)


def add_category(request):
    if request.method == "POST":
        name = request.POST['name']

        Category.objects.create(name=name)
        messages.success(request, "Category added")
        return redirect('view_category')
    return render(request, 'myadmin/add_category.html', locals())


def view_category(request):
    category = Category.objects.all()
    return render(request, 'myadmin/view_category.html', locals())


def edit_category(request, pid):
    category = Category.objects.get(id=pid)
    if request.method == "POST":
        name = request.POST['name']
        category.name = name

        category.save()
        messages.success(request,'Category Updated')
    return render(request, 'myadmin/edit_category.html', locals())

def delete_category(request, pid):
    category = Category.objects.get(id=pid)
    category.delete()
    return redirect('view_category')


def add_product(request):
    category = Category.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        price = request.POST['price']
        cat = request.POST['category']
        discount = request.POST['discount']
        desc = request.POST['desc']
        image = request.FILES.get('image') 
        
        catobj = Category.objects.get(id=cat)
        Product.objects.create(name=name, price=price, discount=discount, category=catobj, description=desc, image=image)
        messages.success(request, "Product added")
    return render(request, 'myadmin/add_product.html', locals())

def view_product(request):
    product = Product.objects.all()
    return render(request, 'myadmin/view_product.html', locals())

def edit_product(request, pid):
    product = Product.objects.get(id=pid)
    category = Category.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        price = request.POST['price']
        cat = request.POST['category']
        discount = request.POST['discount']
        desc = request.POST['desc']
        try:
            image = request.FILES['image']
            product.image = image
            product.save()
        except:
            pass
        catobj = Category.objects.get(id=cat)
        Product.objects.filter(id=pid).update(name=name, price=price, discount=discount, category=catobj, description=desc)
        messages.success(request, "Product Updated")
    return render(request, 'myadmin/edit_product.html', locals())

def delete_product(request, pid):
    product = Product.objects.get(id=pid)
    product.delete()
    messages.success(request, "Product Deleted")
    return redirect('view_product')
  
@login_required
def c_users(request):
    users = CustomUser.objects.all() 
    return render(request, 'myadmin/c_users.html', {'users': users})

@login_required
def user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active 
    user.save()
    return redirect('c_users')  

def view_carousel(request):
    carousel = Carousel.objects.all()
    return render(request, 'myadmin/view_carousel.html',{'carousel':carousel})

def add_carousel(request):
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        image = request.FILES.get('image') 

        Carousel.objects.create(title=title, description=description, image=image)
        messages.success(request, "Carousel added")
    
    return render(request, 'myadmin/add_carousel.html')

def edit_carousel(request, pid):
    carousel = Carousel.objects.get(id=pid)
   
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        
        try:
            image = request.FILES['image']
            carousel.image = image
            carousel.save()
        except:
            pass
        
        Carousel.objects.filter(id=pid).update(title=title, description=description)
        messages.success(request, "Carousel Updated")
        return redirect('view_carousel')
    return render(request, 'myadmin/eidt_carousel.html', locals())  

def delete_carousel(request,pid):
    carousel = Carousel.objects.get(id=pid)
    carousel.delete()
    return redirect('view_carousel')
    return render(request, 'myadmin/delete_carousel.html')

from order.models import Orders

def admin_order(request):
    
    orders = Orders.objects.select_related('address', 'cart', 'user').order_by('-created').all()

    return render(request, 'myadmin/admin_order.html', {'orders': orders})

def admin_update_order_status(request):
    if request.method == "POST":
        orders = Orders.objects.all()
        for order in orders:
            new_status = request.POST.get(f"status_{order.id}")
            if new_status and new_status != order.status:
                order.status = new_status
                order.save()
                messages.success(request, f"Order {order.id} status updated to {new_status}.")
        return redirect('admin_order')
    return redirect('admin_order')



def approve_return(request, order_id):
    order = get_object_or_404(Orders, id=order_id)

    
    if not request.user.is_staff:
        messages.error(request, "Permission denied: Only staff can approve returns.")
        return redirect('admin_order')

    # Check if return request conditions are met
    if not order.return_requested:
        messages.error(request, "Return request not initiated for this order.")
        return redirect('admin_order')

    if order.return_approved:
        messages.error(request, "This order's return has already been approved.")
        return redirect('admin_order')

    if order.is_refunded:
        messages.error(request, "This order has already been refunded.")
        return redirect('admin_order')

    try:

        # Handle wallet update if order was paid
        if order.is_paid:

            order.return_approved = True
            order.status = "Returned"
            order.is_refunded = True  # Mark as refunded
            order.save()
            # Update user's wallet
            order.user.wallet += order.total
            order.user.save()
            messages.success(request, "Return request approved and amount added to wallet.")
            logger.info(f"Return approved for Order ID {order_id}. Wallet updated for user {order.user.id}.")
        else:
            messages.warning(request, "Order was not paid. No amount added to wallet.")

        # Additional logging

    except Exception as e:
        messages.error(request, f"An error occurred while approving the return: {e}")

    return redirect('admin_order')
