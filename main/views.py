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
    #Retrieving the product based on p-id
    product = Product.objects.get(id=pid)

    #get or create the cart base on user
    cart,created= Cart.objects.get_or_create(user=request.user)
    
    #get or create cartitem based on cart 
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
  
    #initial quantity of 1
    if not created:
        #alredy have just added
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_view') 

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    #cartitem fetch with user cart
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
#################################
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Address, Cart, Order, Payment
from django.contrib import messages
import hmac
import hashlib
import json

# Razorpay client setup
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Add Address View
@login_required
def add_address(request):
    if request.method == 'POST':
        address_line = request.POST.get('address_line')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        # Create a new address for the logged-in user
        Address.objects.create(
            user=request.user,
            address_line=address_line,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country
        )
        messages.success(request, "Address added successfully!")
        return redirect('checkout')

    return render(request, 'main/add_address.html')

# Checkout View
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    address = Address.objects.filter(user=request.user).last()

    if not address:
        return redirect('add_address')  # Redirect to address addition if no address exists

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        # Create the order
        order = Order.objects.create(
            cart=cart,
            address=address,
            payment_method=payment_method,
            is_paid=False
        )

        if payment_method == 'RAZORPAY':
            amount_in_paise = int(cart.total_price * 100)  # Razorpay expects the amount in paise
            razorpay_order = razorpay_client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_capture': '1'
            })
            razorpay_order_id = razorpay_order['id']

            # Create a payment object
            Payment.objects.create(
                order=order,
                payment_id=razorpay_order_id,
                amount=cart.total_price
            )

            # Send data to template for Razorpay payment
            context = {
                'order': order,
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'order_id': razorpay_order_id,
                'amount': amount_in_paise,
            }
            return render(request, 'main/razorpay_payment.html', context)

        elif payment_method == 'COD':
            # Handle Cash on Delivery (COD)
            Payment.objects.create(
                order=order,
                payment_id='COD',
                amount=cart.total_price,
                payment_status='Completed'
            )
            order.is_paid = True
            order.save()
            return redirect('order_success')

    return render(request, 'main/checkout.html', {'cart': cart, 'address': address})

# Razorpay Callback View
@csrf_exempt
@login_required
def razorpay_callback(request):
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        try:
            # Verify the signature
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

            payment = Payment.objects.get(payment_id=razorpay_order_id)
            payment.payment_id = razorpay_payment_id
            payment.payment_status = 'Completed'
            payment.save()

            # Mark the order as paid
            order = payment.order
            order.is_paid = True
            order.save()

            return redirect('order_success')

        except razorpay.errors.SignatureVerificationError:
            return redirect('order_failed')


################################
# after payment i wil use later
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