from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
import stripe
from django.contrib import messages
from main.models import Cart
from order.models import Addresss, Orders, Payments

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout_view(request):
    """Handles the checkout process, including address selection and payment method."""
    
    # Get the user's cart
    cart = get_object_or_404(Cart, user=request.user)

    # Check if the cart is empty and redirect to cart view if it is
    if not cart.cartitem_set.exists():
        messages.warning(request, "Your cart is empty. Please add items before proceeding to checkout.")
        return redirect('cart_view')  # Redirect to cart page if the cart is empty

    # Calculate total price in cents for Stripe
    total_price = int(cart.total_price * 100)
    addresses = Addresss.objects.filter(user=request.user).order_by('-id')[:3]

    # Redirect to add address if no addresses exist
    if not addresses.exists():
        return redirect(f"{reverse('add_address')}?total_price={total_price}")

    # Handle the form submission for address and payment selection
    if request.method == "POST":
        payment_method = request.POST.get('payment_method')
        address_id = request.POST.get('address_id')

        # Check if an address was selected
        if not address_id:
            messages.warning(request, "Please select an address to proceed.")
            return redirect('checkout_selection')  # Redirect to the same page

        user_selected_address = get_object_or_404(Addresss, id=address_id, user=request.user)

        # Create an order
        order = Orders.objects.create(
            cart=cart,
            address=user_selected_address,
            user=request.user,
            total=cart.total_price,
            payment_method=payment_method,
            is_paid=False
        )

        # Process payment based on the selected method
        if payment_method == 'STRIPE':
            return handle_stripe_payment(request, order, total_price)
        elif payment_method == 'COD':
            order.is_paid = False
            order.save()
            cart.cartitem_set.all().delete()  # Empty the cart after order creation
            messages.success(request, "Your order has been placed successfully with Cash on Delivery.")
            return redirect('order_confirmation', order_id=order.id)

    # Render the checkout selection page
    return render(request, 'order/checkout_selection.html', {
        'total_price': total_price / 100,  # Convert to dollars for display
        'addresses': addresses
    })


def handle_address_creation(request):
    """Handles creation of a new address during the checkout process."""
    
    total_price = request.GET.get('total_price')
    if request.method == "POST" and request.POST.get('action') == 'create_address':
        # Collect address details from the form
        address_line = request.POST.get('address_line')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        # Create new address
        Addresss.objects.create(
            user=request.user,
            address_line=address_line,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country
        )
        messages.success(request, "Address created successfully.")
        return redirect('checkout_selection')  # Update this to match the URL name

    # Render the add address form
    return render(request, 'order/add_address.html', {'total_price': total_price})


def handle_stripe_payment(request, order, total_price):
    """Creates a Stripe payment intent and renders the Stripe payment page."""
    
    try:
        # Create a Stripe payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=total_price,
            currency='INR',  # Updated currency to INR
            metadata={'order_id': order.id}
        )

        # Create a payment record with status 'Pending'
        Payments.objects.create(
            order=order,
            payment_id=payment_intent['id'],
            amount=total_price / 100,  # Convert to dollars for storage
            payment_status='Pending'
        )

        # Render Stripe payment page with client secret for Stripe.js
        return render(request, 'order/stripe_payment.html', {
            'client_secret': payment_intent['client_secret'],
            'amount': total_price / 100,  # Display in dollars
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
    """Displays order confirmation and checks payment status for Stripe payments."""
    
    order = get_object_or_404(Orders, id=order_id)

    # If Stripe payment, check its final status
    if order.payment_method == 'STRIPE':
        try:
            payment = Payments.objects.get(order=order)
            payment_intent = stripe.PaymentIntent.retrieve(payment.payment_id)
            if payment_intent.status == 'succeeded':
                order.is_paid = True
                payment.payment_status = 'Succeeded'
                order.save()
                payment.save()
                order.cart.cartitem_set.all().delete()  # Empty the cart after payment
                messages.success(request, "Your payment was successful!")
            else:
                messages.warning(request, f"Payment not completed: {payment_intent.status}. Please try again.")
        except Exception as e:
            messages.error(request, f"Error fetching payment status: {str(e)}")

    # Render the order confirmation page
    return render(request, 'order/order_confirmation.html', {'order': order})
