from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import slugify  
from accounts.models import UserProfile
from vendor.models import Vendor
from .forms import VendorForm
from accounts.forms import UserProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_user_vendor
from menu.models import Category, FoodItem
from .utils import get_vendor
from menu.forms import CategoryForm, FoodItemForm
# Create your views here.
 
@login_required(login_url = 'login')
@user_passes_test(check_user_vendor)
def vProfile(request):
    profile = get_object_or_404(UserProfile, user = request.user)
    vendor = get_object_or_404(Vendor, user = request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance = profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance = vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, "Profile Updated successfully!")
            return redirect('vProfile')
        else:
            print(profile_form.errors, vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)
    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor

    }
    return render(request, 'vendor/vprofile.html', context)

@login_required(login_url = 'login')
@user_passes_test(check_user_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor = vendor).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/menu_builder.html', context)

@login_required(login_url = 'login')
@user_passes_test(check_user_vendor)
def foodItems_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    foodItems = FoodItem.objects.filter(vendor = vendor, category = category)
    context = {
        'fooditems': foodItems,
        'category': category,
    }
    return render(request, 'vendor/foodItems_by_category.html', context)

@login_required(login_url = 'login')
@user_passes_test(check_user_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit = False)
            category.vendor = get_vendor(request)
            category.slug = slugify(form.cleaned_data['category_name'])
            category.save()
            messages.success(request, "Category addedd successfully!")
            return redirect('menu_builder')
    else:
        form = CategoryForm()
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_user_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('menu_builder')
    else:
        form = CategoryForm(instance=category)
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'vendor/edit_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_user_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    name = category.category_name
    category.delete()
    messages.success(request, '{} was successfully deleted!'.format(name))
    return redirect('menu_builder')


@login_required(login_url='login')
@user_passes_test(check_user_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, 'Food Product added successfully!')
            return redirect('foodItems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        # modify this form
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_food.html', context)

@login_required(login_url='login')
@user_passes_test(check_user_vendor)
def edit_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, 'Food Product updated successfully!')
            return redirect('foodItems_by_category', food.category.id)
        else:
            print(form.errors)

    else:
        form = FoodItemForm(instance=food)
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
        'food': food,
    }
    return render(request, 'vendor/edit_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_user_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, 'Food Product has been deleted successfully!')
    return redirect('foodItems_by_category', food.category.id)
