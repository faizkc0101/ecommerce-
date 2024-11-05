from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from main.models import Cart,CartItem
from order.models import Addresss, Orders, Payments
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout_view(request):
    
    cart = get_object_or_404(Cart, user=request.user)
    items = CartItem.objects.filter(cart=cart)

    if not cart.cartitem_set.exists():
        messages.warning(request, "Your cart is empty. Please add items before proceeding to checkout.")
        return redirect('cart_view')  

    
    total_price = int(cart.total_price['total_discounted'] * 100)
    #lates 3 addess to face
    addresses = Addresss.objects.filter(user=request.user).order_by('-id')[:3]


    if not addresses.exists():
        return redirect('add_address')
        

   
    if request.method == "POST":
        payment_method = request.POST.get('payment_method')
        address_id = request.POST.get('address_id')


        if not address_id:
            messages.warning(request, "Please select an address to proceed.")
            return redirect('checkout_selection') 

        user_selected_address = get_object_or_404(Addresss, id=address_id, user=request.user)

        order = Orders.objects.create(
            cart=cart,
            address=user_selected_address,
            user=request.user,
            total=cart.total_price['total_discounted'],
            payment_method=payment_method,
            is_paid=False
        )

        if payment_method == 'STRIPE':
            return handle_stripe_payment(request, order, total_price)


        elif payment_method == 'COD':
            order.is_paid = False
            order.save()
            cart.cartitem_set.all().delete()
            messages.success(request, "Your order has been placed successfully with Cash on Delivery.")
            return redirect('order_confirmation', order_id=order.id)


    return render(request, 'order/checkout_selection.html', {
        'total_price': total_price / 100, 
        'addresses': addresses ,'items':items,'cart':cart})


def handle_address_creation(request):
    
    total_price = request.GET.get('total_price')

    if request.method == "POST" and request.POST.get('action') == 'create_address':
       
        address_line = request.POST.get('address_line')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')


        Addresss.objects.create(
            user=request.user,
            address_line=address_line,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country
        )
        messages.success(request, "Address created successfully.")
        return redirect('checkout_selection')  

    return render(request, 'order/add_address.html', {'total_price': total_price})


def handle_stripe_payment(request, order, total_price):
    
    try:
      
        payment_intent = stripe.PaymentIntent.create(
            amount=total_price,
            currency='INR',  
            metadata={'order_id': order.id}
        )

        
        Payments.objects.create(
            order=order,
            payment_id=payment_intent['id'],
            amount=total_price / 100,
            payment_status='Pending'
        )

       
        return render(request, 'order/stripe_payment.html', {
            'client_secret': payment_intent['client_secret'],
            'amount': total_price / 100,  
            'order_id': order.id,
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
        })
    except Exception as e:
        messages.error(request, f"Error creating payment intent: {str(e)}")
        return render(request, 'order/checkout_selection.html', {
            'total_price': total_price / 100,
            'addresses': Addresss.objects.filter(user=order.cart.user)
        })


def order_confirmation(request, order_id):
   
    
    order = get_object_or_404(Orders, id=order_id)

    
    if order.payment_method == 'STRIPE':
        try:
            payment = Payments.objects.get(order=order)
            payment_intent = stripe.PaymentIntent.retrieve(payment.payment_id)
            if payment_intent.status == 'succeeded':
                order.is_paid = True
                payment.payment_status = 'Succeeded'
                order.save()
                payment.save()
                order.cart.cartitem_set.all().delete()  
                messages.success(request, "Your payment was successful!")
            else:
                messages.warning(request, f"Payment not completed: {payment_intent.status}. Please try again.")
        except Exception as e:
            messages.error(request, f"Error fetching payment status: {str(e)}")


    return render(request, 'order/order_confirmation.html', {'order': order})

def my_order(request):
    orders = Orders.objects.filter(user=request.user).order_by('-created')
    return render(request,'order/my_order.html',{'orders': orders})



def user_order_track(request, order_id):
   
    order = get_object_or_404(Orders, id=order_id, user=request.user)
    order_status_choices = Orders.ORDER_STATUS 

    return render(request, "order/user-order-track.html", {
        'order': order,
        'order_status_choices': order_status_choices,
       
    })


def change_order_status(request, pid):
   
    order = get_object_or_404(Orders, id=pid)
    status = request.GET.get('status')
  
    allowed_transitions = {
        'Pending': ['Cancelled'],
        'Delivered': ['Return'],
    }

    if status in allowed_transitions.get(order.status, []):
        order.status = status
        order.save()
        messages.success(request, f"Order status updated to '{status}'.")
    else:
        messages.error(request, f"Cannot change status from '{order.status}' to '{status}'.")

    return redirect('my_order')


def request_return(request, order_id):
    order = get_object_or_404(Orders, id=order_id, user=request.user)

    # Only allow return requests if the order is delivered and not already requested
    if order.is_paid:
        if order.status == "Delivered" and not order.return_requested and not order.is_refunded:
            order.return_requested = True
            order.save()
            messages.success(request, "Return request submitted successfully.")
    else:
        messages.error(request, "payment not comlted")

    return redirect('my_order')  # Change to your dashboard URL