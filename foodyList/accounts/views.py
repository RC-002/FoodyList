from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from accounts.models import User, UserProfile
from accounts.utils import detect_user, send_verification_email
from .forms import UserForm
from vendor.forms import VendorForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

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

            #Send verification mail
            send_verification_email(request, user)
            messages.success(request, "Your account has been created! Wait for the confirmation email")
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
            #Send verification mail              
            vendor.save()
            mail_subject = 'Verify your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template) 
            messages.success(request, "Your restaurant account has been created! Wait for the confirmation email")
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

def activate(request, uidb64, token):
    #activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk = uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account verified!")
    else:
        messages.error(request, "Invalid activation link")
    return redirect('myAccount')


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

def forgot_password(request):
    if request.method == "POST":
        email = request.POST['email']
        if User.objects.filter(email = email).exists():
            user = User.objects.get(email__exact = email)

            #send reset password email
            mail_subject = 'Reset your Password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)        
            messages.success(request, "Password reset link sent to your email address")
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request, uidb64, token):
    #validate the user
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk = uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']  = uid
        messages.info(request,'Reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has expired')
        return redirect('forgot_password')

def reset_password(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk = pk)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login') 
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')
