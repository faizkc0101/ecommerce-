from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from main.models import *


def home(request):
    #admin can  add carousel from backend 
    carousel = Carousel.objects.all()
    latest_products = Product.objects.all().order_by('-id')[:10]
    return render(request,'main/home.html',{'carousel':carousel,'latest_products':latest_products})


def about(request):
    return render(request, 'main/about.html')


def contact(request):
    return render(request, 'main/contact.html')

from django.core.paginator import Paginator
# show product all or catgory wase
def user_product(request, pid):
    # All products
    if pid == 0:
        product = Product.objects.all()
        selected_category = "All category"
    # Filter by category
    else:
        category = get_object_or_404(Category, id=pid) 
        product = Product.objects.filter(category=category)
        selected_category = category.name 
   
    allcategory = Category.objects.all() 

    if not product.exists():
        messages.warning(request, "No products available in this category.")

    # Paginator
    paginator = Paginator(product, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

   
    context = {
        'page_obj': page_obj, 
        'allcategory': allcategory,
        'selected_category': selected_category,
    }
    return render(request, "main/user-product.html", context)


#single poduct 
def product_detail(request, pid):
    product = get_object_or_404(Product, id=pid)
    
    # latest  10 product
    latest_products = Product.objects.exclude(id=pid).order_by('-id')[:4]

    context = {'product': product,'latest_products': latest_products}

    return render(request, "main/product_detail.html", context)


@login_required(login_url='user_login')
def add_to_cart(request, pid):
    product = Product.objects.get(id=pid)

    if request.user.is_staff: 
        messages.error(request, "Admins cannot add products to the cart.")
        return redirect('cart_view')

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
  
    # Initial quantity of 1
    if not created:
        # Already have just added
        cart_item.quantity += 1
    cart_item.save()

    messages.success(request, f"{product.name} has been added to your cart.")
    return redirect('cart_view')


@login_required(login_url='user_login')
def cart_view(request):

    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    total = cart.total_price
    
    return render(request, 'main/cart.html', {'cart': cart, 'items': items, 'total': total})


@login_required(login_url='user_login')
def update_cart_item(request, pid, action):
    cart = Cart.objects.get(user=request.user)
    cart_item = CartItem.objects.get(cart=cart, product_id=pid)

    if action == 'incre':
        cart_item.quantity += 1
    elif action == 'decre' and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()

    return redirect('cart_view')


@login_required
def remove_cart_item(request, pid):
    cart = Cart.objects.get(user=request.user)
    cart_item = CartItem.objects.get(cart=cart, product_id=pid)
    cart_item.delete()
    messages.warning(request,'remove product from cart')
    return redirect('cart_view') 
from django.shortcuts import render
from django.db.models import Q
from .models import Product

def search(request):
    query = request.GET.get('keyword', '')
    products = Product.objects.all()  # Initialize products with all products

    if query:
        try:
            # Filter products by name or category
            products = products.filter(
                Q(name__icontains=query) | Q(category__name__icontains=query)
            )
        except Exception as e:
            pass
    return render(request, 'main/search.html', {'products': products, 'query': query})
