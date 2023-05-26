
from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from .models import Cart,Product,Customer,Order,Address,Wishlist
from django.db.models import F,Sum
from django.http import Http404
from django.views.decorators.cache import cache_control,never_cache
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json
from django.http import Http404,JsonResponse

@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def cart(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    
    cart_items = cart_items.annotate(item_total=F('quantity') * F('product__price'))
    
    
    subtotal   = cart_items.aggregate(subtotal=Sum('item_total'))['subtotal']

   
    for cart_item in cart_items:
        cart_item.total_price = cart_item.item_total
        cart_item.save()
    shipping_cost = 10 
    
    total = subtotal + shipping_cost if subtotal else 0
    
    context = {
        'cart_items': cart_items,
        'subtotal'  : subtotal,
        'total'     : total,
    }
    return render(request, 'cart.html', context)


@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect('product_not_found')

    quantity = request.POST.get('quantity')

    if not quantity:
        quantity = 1

    cart, created = Cart.objects.get_or_create(
        product=product,
        user=request.user,
        defaults={'quantity': 0}
    )

    cart.quantity += quantity
    cart.save()
    
    return redirect('cart')

@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def remove_from_cart(request, cart_item_id):
    try:
        cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
        cart_item.delete()
    except Cart.DoesNotExist:
        pass
    
    return redirect('cart')


@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    
    cart_items = cart_items.annotate(item_total=F('quantity') * F('product__price'))
    
    subtotal = cart_items.aggregate(subtotal=Sum('item_total'))['subtotal']

    shipping_cost = 10 
    
    total = subtotal + shipping_cost if subtotal else 0
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
    }
    return render(request, 'checkout.html', context)

    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def productdetails(request ,product_id=None ):
    context ={}
    try:
        context['product'] = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise Http404("Product doesnot exst")
  
    return render(request, 'detail.html',context)
    

def edit_profile(request):
    try:
        customer = Customer.objects.get(id=request.user.id)
    except Customer.DoesNotExist:
        return redirect('home')

    if request.method == 'POST':
        customer.username   =   request.POST.get('username')
        customer.email      =   request.POST.get('email')
        customer.number     =   request.POST.get('number')
        password            =   request.POST.get('password1')
        
        if password:
            customer.set_password(password)
        
        customer.save()
        return redirect('home')
    orders = Order.objects.filter(user=request.user.id).order_by('id')

    context = {
        'customer': customer,
        'orders':orders
    
    }

    return render(request, 'profile.html', context)

@login_required
def placeorder(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    
    cart_items = cart_items.annotate(item_total=F('quantity') * F('product__price'))
    
    subtotal = cart_items.aggregate(subtotal=Sum('item_total'))['subtotal']

    shipping_cost = 10 
    
    total = subtotal + shipping_cost if subtotal else 0
    
    if request.method == 'POST':
        first_name    =    request.POST.get('firstname')
        last_name     =    request.POST.get('lastname')
        email         =    request.POST.get('email')
        number        =    request.POST.get('number')
        address1      =    request.POST.get('address1')
        address2      =    request.POST.get('address2')
        country       =    request.POST.get('country')
        state         =    request.POST.get('state')
        city          =    request.POST.get('city')
        zip_code      =    request.POST.get('zip')
        payment       =    request.POST.get('payment')
       

        if not email or not first_name or not last_name or not number or not address1 or not address2 or not country or not state or not city or not zip or not payment :
            messages.error(request, 'Please input all the details!!!')
            return redirect('checkout')
        
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        
        
        
        address = Address.objects.create(
            user        =  user,
            first_name   =  first_name,
            last_name    =  last_name,
            email       =  email,
            number      =  number,
            address1    =  address1,
            address2    =  address2,
            country     =  country,
            state       =  state,
            city        =  city,
            zip_code    =  zip_code
        )

        for cart_item in cart_items:
            order = Order.objects.create(

                user          =     user,
                address       =     address,
                product       =     cart_item.product,
                amount        =     total,
                payment_type  =     payment,
                quantity      =     cart_item.quantity,
                image         =     cart_item.product.image  
            )
            order.save()
        address.save()
        cart_items.delete()
        return redirect('success')

def success(request):
    return render(request,'placeorder.html')



def update_cart(request, product_id):
    cart_item = get_object_or_404(Cart, product_id=product_id, user=request.user)
    
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity'))
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({'message': 'Invalid quantity.'}, status=400)
    
    if quantity < 1:
        return JsonResponse({'message': 'Quantity must be at least 1.'}, status=400)

    cart_item.quantity = quantity
    cart_item.save()

    return JsonResponse({'message': 'Cart item updated.'}, status=200)


    
def order(request):
    if 'admin' in request.session:
        orders = Order.objects.all().order_by('id')
        
       
        paginator = Paginator(orders, per_page=1) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'orders': page_obj,
        }
        return render(request, 'orders.html', context)
    else:
        return redirect('admin')


def updateorder(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')

       
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return redirect('order')  

      
        order.status = status
        order.save()

        return redirect('order') 

    return redirect('admin')


def wishlist(request):
    user = request.user
    wishlist_items = Wishlist.objects.filter(user=user)

    context = {
        'wishlist_items': wishlist_items
    }

    return render(request, 'wishlist.html', context)


def add_to_wishlist(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect('product_not_found')

    wishlist, created = Wishlist.objects.get_or_create(
        product=product,
        user=request.user
    )
    wishlist.save()

    return redirect('wishlist')


def remove_from_wishlist(request, wishlist_item_id):
    try:
        wishlist_item = Wishlist.objects.get(id=wishlist_item_id, user=request.user)
        wishlist_item.delete()
    except Cart.DoesNotExist:
        pass
    
    return redirect('wishlist')

def cancel_order(request,order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=order_id)
            order.status = 'cancelled'
            order.save()
        except Order.DoesNotExist:
            pass  

    return redirect('edit_profile')

def forgot_password(request):
    pass

def reset_password(request):
    pass
    




