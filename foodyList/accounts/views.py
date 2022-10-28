from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from accounts.models import User, UserProfile
from accounts.utils import detect_user
from .forms import UserForm
from vendor.forms import VendorForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

#Restrict the vendor from accessing the customer Dashboard
def check_user_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied
    
#Restrict the customer from accessing the Vendor Dashboard
def check_user_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied

# Create your views here.
def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('dashboard')
    elif request.method == 'POST':
        # print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            # print("valid")
            password = form.cleaned_data['password']
            user = form.save(commit = False)
            user.set_password(password)
            user.role = User.CUSTOMER
            user.save()
            messages.error(request, "Your account has been registered successfully!")
            return redirect('registerUser')
        else:
            print("not valid")
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('dashboard')
    elif request.method == 'POST':
        # store the data and create user
        form = UserForm(request.POST)
        vForm = VendorForm(request.POST, request.FILES)
        if form.is_valid() and vForm.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit = False)
            user.set_password(password)
            user.role = User.VENDOR
            user.save()
            vendor = vForm.save(commit = False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user = user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(request, "Restaurant registered successfully!")
            return redirect('registerVendor')
        else:
            print("invalid form")
    else:
        form = UserForm()
        vForm = VendorForm()
    context = {
        'form': form,
        'v_form': vForm,
    }
    return render(request, 'accounts/registerVendor.html', context)

def login(request):
    if request.user.is_authenticated:
        messages.success(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email = email, password = password)
        
        if user is not None:
            auth.login(request, user)
            messages.success(request, "Welcome!")
            return redirect('myAccount')
        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')
    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request, 'You are now logged out')
    return redirect('login') 

@login_required(login_url = 'login')
def myAccount(request):
    user = request.user
    redirectUrl = detect_user(user)
    return redirect(redirectUrl)

@login_required(login_url = 'login')
@user_passes_test(check_user_customer)
def customerDashboard(request):
    return render(request, 'accounts/customerDashboard.html')

@login_required(login_url = 'login')
@user_passes_test(check_user_vendor)
def VendorDashboard(request):
    return render(request, 'accounts/VendorDashboard.html')

