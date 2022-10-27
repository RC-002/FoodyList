from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import User
from .forms import UserForm

# Create your views here.
def registerUser(request):
    if request.method == 'POST':
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
    return render(request, 'accounts/registerVendor.html')