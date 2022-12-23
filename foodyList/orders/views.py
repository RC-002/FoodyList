from django.shortcuts import render, redirect
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amounts
from .forms import OrderForm
from .models import Order
from .utils import generate_order_number
# Create your views here.

def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    vendors_ids = []
    for i in cart_items:
        if i.fooditem.vendor.id not in vendors_ids:
            vendors_ids.append(i.fooditem.vendor.id)
    
    # for i in cart_items:
    #     fooditem = FoodItem.objects.get(pk=i.fooditem.id, vendor_id__in=vendors_ids)
    #     v_id = fooditem.vendor.id
    #     if v_id in k:
    #         subtotal = k[v_id]
    #         subtotal += (fooditem.price * i.quantity)
    #         k[v_id] = subtotal
    #     else:
    #         subtotal = (fooditem.price * i.quantity)
    #         k[v_id] = subtotal  
        

    subtotal = get_cart_amounts(request)['subtotal']
    total_tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pincode = form.cleaned_data['pincode']
            order.user = request.user
            order.total = grand_total
            # order.tax_data = json.dumps(tax_data)
            # order.total_data = json.dumps(total_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save() # order id/ pk is generated
            order.order_number = generate_order_number(order.id)
            # order.vendors.add(*vendors_ids)
            order.save()
            context = {
                'order': order,
                'cart_items': cart_items,
            }
            return render(request, 'orders/place_order.html', context)
        else:
            print(form.errors)
    return render(request, 'orders/place_order.html')


def confirmation(request):
    return render(request,"orders/confirmation.html")