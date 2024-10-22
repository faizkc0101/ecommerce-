from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser,UserProfile
from django.contrib.auth.decorators import login_required
import random
from django.conf import settings
from django.contrib import messages

from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.cache import cache_control
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import update_session_auth_hash 


def user_register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_field = request.POST.get('phone_field')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        address = request.POST.get('address')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/register.html')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'accounts/register.html')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'accounts/register.html')

        try:
            otp = random.randint(1000, 9999)
            request.session['otp'] = otp
            request.session['otp_expiry'] = (timezone.now() + timedelta(minutes=10)).isoformat()

            send_mail(
                'Verify your email',
                f'Your OTP for verification is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )

            request.session['user_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'phone_field': phone_field,
                'email': email,
                'username': username,
                'password': password,
                'address':address,
            }

            messages.success(request, "OTP has been sent to your email for verification.")
            return redirect('verify') 
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return render(request, 'accounts/user_register.html')

    return render(request, 'accounts/register.html')

def verify(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        otp_expiry_str = request.session.get('otp_expiry')

        otp_expiry = timezone.datetime.fromisoformat(otp_expiry_str) 

        if timezone.now() > otp_expiry:
            messages.error(request, "OTP has expired. Please register again.")
            return redirect('user_register')

        if str(stored_otp) == entered_otp:
            user_data = request.session.get('user_data')
            if user_data:
                user = CustomUser.objects.create_user(
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    email=user_data['email'],
                    username=user_data['username'],
                    password=user_data['password'],
                    phone_field =user_data['phone_field'],
                )
                
              
                UserProfile.objects.create(
                    user=user,
                    address=user_data['address']
                )

                user.is_active = True  
                user.save()

                request.session.flush()

                messages.success(request, "OTP verified successfully! You can now log in.")
                return redirect('user_login')
            else:
                messages.error(request, "User data not found. Please register again.")
                return redirect('user_register')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'accounts/verify.html')


def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are logged in')
            return redirect('main')
        else:
            messages.error(request, 'Invalid login credentials')

    return render(request, 'accounts/login.html')


@login_required(login_url='user_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_logout(request):
    logout(request)
    messages.success(request, 'You are logged out')
    return redirect('user_login')

def generate_reset_token(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token


def forgetpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = CustomUser.objects.get(email=email)
            uid, token = generate_reset_token(user)

            reset_link = f'{request.scheme}://{request.get_host()}/accounts/reset/{uid}/{token}/'
            send_mail(
                'Reset Your Password',
                f'Hello {user.first_name},\n\nTo reset your password, click the link below:\n{reset_link}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )
            messages.success(request, 'A password reset link has been sent to your email.')
            return redirect('user_login')
        except CustomUser.DoesNotExist:
            messages.error(request, 'No account found with this email.')

    return render(request, 'accounts/forgetpassword.html')


def newpassword(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)

        if not default_token_generator.check_token(user, token):
            messages.error(request, 'The password reset link is invalid or has expired.')
            return redirect('forgetpassword')

        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 and password2:
                if password1 == password2:
                    user.set_password(password1)
                    user.save()
                    messages.success(request, 'Your password has been reset successfully.')
                    return redirect('user_login')
                else:
                    messages.error(request, 'Passwords do not match.')
            else:
                messages.error(request, 'Please enter both passwords.')

        return render(request, 'accounts/newpassword.html', {'username': user.username})

    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('forgetpassword')


@login_required
def profile(request):
   
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admindashboard')  
    
    data = UserProfile.objects.get(user=request.user)

    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        address = request.POST['address']
        phone_field = request.POST['phone_field']
        
        if 'image' in request.FILES:
            image = request.FILES['image']
            data.image = image
            data.save()

       
       
        UserProfile.objects.filter(id=data.id).update(phone_field=phone_field, address=address)

        messages.success(request, "Profile updated")
        return redirect('profile')

    return render(request, 'accounts/profile.html', locals())




def change_password(request):
    if request.method == 'POST':
        o = request.POST.get('old')  
        n = request.POST.get('new')   
        c = request.POST.get('confirm')  

        user = authenticate(email=request.user.email, password=o) 

        if user:
            if n == c:
                user.set_password(n)  
                user.save()  

                
                update_session_auth_hash(request, user)

                messages.success(request, "Password Changed")
                return redirect('main')
            else:
                messages.error(request, "New passwords do not match")
                return redirect('change_password')
        else:
            messages.error(request, "Invalid old password")
            return redirect('change_password')

    return render(request, 'accounts/change_password.html')
