from django.shortcuts import render,redirect
from main.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def adminLogin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        try:
            if user.is_staff:
                login(request, user)
                messages.success(request,'User login successfully')
                return redirect('admindashboard')
            else:
                messages.error(request,'Invalid Credentials')
                
        except:
             messages.error(request,'Invalid Credentials')
             
    return render(request, 'myadmin/admin_login.html',locals())
 

def admin_dashboard(request):
    return render(request, 'myadmin/admin_dashboard.html')


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