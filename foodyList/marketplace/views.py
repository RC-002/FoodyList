from django.shortcuts import render, get_object_or_404
from vendor.models import Vendor
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from django.http import JsonResponse, HttpResponse
from .models import Cart
from .context_processors import get_cart_counter, get_cart_amounts
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_user_customer, check_user_vendor
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.shortcuts import redirect
from accounts.models import UserProfile
from orders.forms import OrderForm
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
                    cartAmounts = get_cart_amounts(request)
                    return JsonResponse({
                    'status': 'Success',
                    'message': 'Increased quantity',
                    'cart_counter': get_cart_counter(request),
                    'qty': chkCart.quantity,
                    'subtotal': cartAmounts['subtotal'], 'tax': cartAmounts['tax'], 'grand_total': cartAmounts['grand_total'], 'tax_dict': cartAmounts['tax_dict'],
                    })
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem = food_item, quantity = 1)
                    cartAmounts = get_cart_amounts(request)
                    return JsonResponse({
                    'status': 'Success',
                    'message': 'Item added',
                    'cart_counter': get_cart_counter(request),
                    'qty': chkCart.quantity,
                    'subtotal': cartAmounts['subtotal'], 'tax': cartAmounts['tax'], 'grand_total': cartAmounts['grand_total'], 'tax_dict': cartAmounts['tax_dict']
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
                    cartAmounts = get_cart_amounts(request)
                    return JsonResponse({'status': 'Success', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'subtotal': cartAmounts['subtotal'], 'tax': cartAmounts['tax'], 'grand_total': cartAmounts['grand_total'], 'tax_dict': cartAmounts['tax_dict']})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have this product in your cart!'})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This Product does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
        
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})

@login_required(login_url = 'login')
@user_passes_test(check_user_customer)
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)

@login_required(login_url = 'login')
@user_passes_test(check_user_customer)
def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # Check if the cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success', 'message': 'Cart item has been deleted!', 'cart_counter': get_cart_counter(request),'cart_amoount': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Cart Item does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})


def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']    
        radius = request.GET['radius']
        keyword = request.GET['keyword']
        fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)
        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)'%(longitude, latitude), srid=4326)
            vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True), 
            user_profile__location__distance_lte=(pnt, D(km=radius))
            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

            for v in vendors:
                v.kms = round(v.distance.km,1)
        vendors_count = vendors.count()
        context = {
            'vendors': vendors,
            'vendor_count': vendors_count,
            'source_location': address
        }
        return render(request, 'marketplace/listings.html', context)


@login_required(login_url = 'login')
@user_passes_test(check_user_customer)
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pincode': user_profile.pincode,
    }
    form = OrderForm(initial=default_values)
    context = {
        'form': form,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/checkout.html', context)