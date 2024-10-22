from django.shortcuts import render,redirect, get_object_or_404
from .models import *
from accounts.models import UserProfile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
 
def home(request):
    return render(request,'main/home.html')

def index(request):
    return render(request,'navigation.html')

def about(request):
    return render(request,'main/about.html')

def main(request):
    #admin can  add carousel from backend 
    carousel = Carousel.objects.all()
    context = {'carousel': carousel}
    return render(request, 'main/index.html',context)

# product fetching function all or category wase
def user_product(request, pid):
    if pid == 0:
        product = Product.objects.all()  # get all prodect 
        selected_category = "All category"
    else:
        category = get_object_or_404(Category, id=pid)  #get wich category we select from id
        product = Product.objects.filter(category=category) #get product with category
        selected_category = category.name 
   
    allcategory = Category.objects.all()  # Get all categories 

    if not product.exists():
        messages.warning(request, "No products available in this category.")

    context = {
        'product': product,
        'allcategory': allcategory,
        'selected_category':selected_category,    
    }
    return render(request, "main/user-product.html", context)

# selected poduct details
def product_detail(request, pid):
    product = get_object_or_404(Product, id=pid)
    
    # fetch latest added 10 product
    latest_products = Product.objects.exclude(id=pid).order_by('-id')[:10]

    context = {
        'product': product,
        'latest_products': latest_products
    }
    return render(request, "main/product_detail.html", context)


@login_required
def add_to_cart(request, pid):
    product = Product.objects.get(id=pid)
    cart,created= Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()

    return redirect('cart_view') 

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    total = cart.total_price
    return render(request, 'main/cart.html', {'cart': cart, 'items': items, 'total': total})


@login_required
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
    return redirect('cart_view')  


def booking(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()
    
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    total = cart.total_price  

    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == "POST":
    
        booking = Booking.objects.create(user=request.user, total=total)
        booking.products.add(*cart_items) 
        cart.cartitem_set.all().delete() 
        messages.success(request, "Your order has been booked successfully!")
        return redirect('home')

    context = {
        'cart_items': cart_items,
        'total': total,
        'user_profile': user_profile,
        'user': request.user,
    }
    return render(request, "main/booking.html", context)

def myOrder(request):
    order = Booking.objects.filter(user=request.user)
    return render(request, "main/my_order.html", locals())

def user_order_track(request, pid):
    order = Booking.objects.get(id=pid)
    orderstatus = ORDER_STATUS
    return render(request, "main/user-order-track.html", locals())

def change_order_status(request, pid):
    order = Booking.objects.get(id=pid)
    status = request.GET.get('status')
    if status:
        order.status = status
        order.save()
        messages.success(request, "Order status changed.")
    return redirect('myorder')