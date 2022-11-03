from django.shortcuts import render, get_object_or_404
from vendor.models import Vendor
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from django.http import JsonResponse, HttpResponse
from .models import Cart
from .context_processors import get_cart_counter
# Create your views here.

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    count = vendors.count()
    context = {
        'vendors': vendors,
        'count': count
    }
    return render(request, 'marketplace/listings.html', context)

def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)

    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset = FoodItem.objects.filter(is_available=True)
        )
    )
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/vendor_detail.html', context)

def add_to_cart(request, food_id=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #check if the food item exists
            try:
                food_item = FoodItem.objects.get(id = food_id)
                #check if food item is already in cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem = food_item)
                    #increase quantity
                    chkCart.quantity+=1
                    chkCart.save()
                    return JsonResponse({
                    'status': 'Success',
                    'message': 'Increased quantity',
                    'cart_counter': get_cart_counter(request),
                    'qty': chkCart.quantity
                    })
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem = food_item, quantity = 1)
                    return JsonResponse({
                    'status': 'Success',
                    'message': 'Item added',
                    'cart_counter': get_cart_counter(request),
                    'qty': chkCart.quantity
                    })
            except:
                return JsonResponse({
                'status': 'Failed',
                'message': 'Food Product does not exist!'
                })
        else:
            return JsonResponse({
            'status': 'Failed',
            'message': 'Invalid Request'
            })
            
    else:
        return JsonResponse({
            'status': 'login_required',
            'message': 'Please login to order food!'
        })

def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if chkCart.quantity > 1:
                        # decrease the cart quantity
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse({'status': 'Success', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have this product in your cart!'})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This Product does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
        
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})