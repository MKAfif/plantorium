
from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from .models import Cart,Product,Customer,Order,Address,Wishlist,Coupon,Images,OrderItem
from app1.models import Category
from django.db.models import F,Sum
from django.http import Http404
from django.views.decorators.cache import cache_control,never_cache
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json
from django.http import Http404,JsonResponse
import secrets
import smtplib
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.db.models import Case, When, Sum,DecimalField
from django.contrib.auth.models import AnonymousUser



@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def cart(request):
    if 'discount' in request.session:
        del request.session['discount']

    if isinstance(request.user, AnonymousUser):
        device_id = request.COOKIES.get('device_id')
        cart_items = Cart.objects.filter(device=device_id).order_by('id')
    else:
        user = request.user
        cart_items = Cart.objects.filter(user=user).order_by('id')

    subtotal = 0
    total_dict = {}

    for cart_item in cart_items:
        if cart_item.quantity > cart_item.product.stock:
            messages.warning(request, f"{cart_item.product.product_name} is out of stock.")
            cart_item.quantity = cart_item.product.stock
            cart_item.save()

        if cart_item.product.category.category_offer:
            item_price = (cart_item.product.price - cart_item.product.category.category_offer) * cart_item.quantity
            total_dict[cart_item.id] = item_price
            subtotal += item_price

        elif cart_item.product.product_offer:
            item_price = (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer/100)) * cart_item.quantity
            total_dict[cart_item.id] = item_price
            subtotal += item_price

        else:
            item_price = cart_item.product.price * cart_item.quantity
            total_dict[cart_item.id] = item_price
            subtotal += item_price

    for cart_item in cart_items:
        cart_item.total_price = total_dict.get(cart_item.id, 0)
        cart_item.save()

    shipping_cost = 10
    total = subtotal + shipping_cost if subtotal else 0
    coupons = Coupon.objects.all()

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        'coupons': coupons
    }

    return render(request, 'cart.html', context)



@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect('product_not_found')

    quantity = request.POST.get('quantity', 1)

    if not quantity:
        quantity = 1

    if isinstance(request.user, AnonymousUser):
        device_id = request.COOKIES.get('device_id')
        if not device_id:
            return JsonResponse({'message': 'Device ID not found.'}, status=400)

        cart_item, created = Cart.objects.get_or_create(device=device_id, product=product)
    else:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

    if created:
        cart_item.quantity = int(quantity)
    else:
        cart_item.quantity += int(quantity)
    cart_item.save()

    return redirect('cart')
   
      

@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
# def remove_from_cart(request, cart_item_id):
#     try:
#         cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
#         cart_item.delete()
#     except Cart.DoesNotExist:
#         pass
    
#     return redirect('cart')

def remove_from_cart(request, cart_item_id):
    try:
        if isinstance(request.user, AnonymousUser):
            device_id = request.COOKIES.get('device_id')
            if not device_id:
                return JsonResponse({'message': 'Device ID not found.'}, status=400)
            cart_item = Cart.objects.get(id=cart_item_id, device=device_id)
        else:
            cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
        cart_item.delete()
    except Cart.DoesNotExist:
        pass
    
    return redirect('cart')



@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def checkout(request):
    if 'email' in request.session:
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        subtotal=0
        for cart_item in cart_items:
            
            if cart_item.product.category.category_offer:
                itemprice2=(cart_item.product.price - cart_item.product.category.category_offer)*(cart_item.quantity)
                subtotal=subtotal+itemprice2
            elif cart_item.product.product_offer:
                itemprice2 =  (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer/100)) * cart_item.quantity
                subtotal=subtotal+itemprice2  
            else: 
                itemprice2=(cart_item.product.price)*(cart_item.quantity)
                subtotal=subtotal+itemprice2
        shipping_cost = 10 
        discount = request.session.get('discount', 0)
        if discount:
            total =  subtotal + shipping_cost - discount if subtotal else 0
        
        else:
            total =  subtotal + shipping_cost  if subtotal else 0


        addresses = Address.objects.filter(user=user)
    
        context = {
            'cart_items'       :  cart_items,
            'subtotal'         :  subtotal,
            'total'            :  total,
            'addresses'        :  addresses,
            'discount_amount'  :  discount,
            'itemprice'        :  itemprice2
        
            
        }
        return render(request, 'checkout.html', context)
    else:
        return redirect ('signup')

    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def productdetails(request, product_id=None):
   
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise Http404("Product does not exist")
    
    discounted_price = None
    offer_price = None
    if product.category.category_offer:
        discounted_price = product.price - product.category.category_offer
    product.discounted_price = discounted_price
    
    
    if product.product_offer:
        offer_price        = product.price -(product.price * product.product_offer/100)
    product.offer_price    = offer_price



    images = Images.objects.filter(product=product)
    context = {
        'product'         : product,
        'images'          : images,
        'discounted_price': discounted_price
    }
    return render(request, 'detail.html', context)
  


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
        profile_photo       =   request.FILES.get('image')
        address_id          =   request.POST.get('id')      

        if profile_photo:
            customer.profile_photo.save(profile_photo.name, profile_photo, save=True)

        if password:
            customer.set_password(password)    
        customer.save()
        messages.success(request,'Updated successfully')
        return redirect('edit_profile')
    
        
   
    addresses        =  Address.objects.filter(user=request.user).order_by('id')
    

    context = {
        'customer'      :  customer,
        'addresses'     :  addresses,
      
      
    
    }

    return render(request, 'testing.html', context)

@login_required
def placeorder(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    
  
    subtotal=0
    for cart_item in cart_items:
        
        if cart_item.product.category.category_offer:
            
            itemprice2=(cart_item.product.price - cart_item.product.category.category_offer)*(cart_item.quantity)
            subtotal=subtotal+itemprice2

        elif cart_item.product.product_offer:
            itemprice2 =  (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer/100)) * cart_item.quantity
            subtotal=subtotal+itemprice2  
            
        else:
            
            itemprice2=(cart_item.product.price)*(cart_item.quantity)
            
            subtotal=subtotal+itemprice2
    shipping_cost = 10 
    total = subtotal + shipping_cost if subtotal else 0
    
    discount = request.session.get('discount', 0)

    if request.method == 'POST':
        payment       =    request.POST.get('payment')
        address_id    =    request.POST.get('addressId')
    
    if not address_id:
        messages.info(request, 'Input Address!!!')
        return redirect('checkout')
    if discount:
        total -= discount 

    address = Address.objects.get(id=request.POST.get('addressId'))

    order = Order.objects.create(
        user          =     user,
        address       =     address,
        amount        =     total,
        payment_type  =     payment,
    )

    for cart_item in cart_items:
        product = cart_item.product
        product.stock -= cart_item.quantity
        product.save()

        order_item = OrderItem.objects.create(
            order         =     order,
            product       =     cart_item.product,
            quantity      =     cart_item.quantity,
            image         =     cart_item.product.image  
        )
    
    cart_items.delete()
    return redirect('success')



def success(request):
    orders = Order.objects.order_by('-id')[:1]
    context = {
        'orders'  : orders,

    }
    return render(request,'placeorder.html',context)





def update_cart(request, product_id):
    cart_item = None
    if isinstance(request.user, AnonymousUser):
        device_id = request.COOKIES.get('device_id')
        if not device_id:
            return JsonResponse({'message': 'Device ID not found.'}, status=400)

        cart_item, created = Cart.objects.get_or_create(device=device_id, product_id=product_id)
    else:
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


 
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache     
def order(request):
    if 'admin' in request.session:
        orders = Order.objects.all().order_by('-id')
        
       
        paginator = Paginator(orders, per_page=10) 
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
        messages.success(request, 'Order status updated successfully.')

        

        return redirect('order') 

    return redirect('admin')




def wishlist(request):

    user = request.user
    if isinstance(user, AnonymousUser):
    
        device_id = request.COOKIES.get('device_id')
        if not device_id:
            return JsonResponse({'message': 'Device ID not found.'}, status=400)
        wishlist_items = Wishlist.objects.filter(device=device_id)
    else:
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

    user = request.user
    if isinstance(user, AnonymousUser):
        device_id = request.COOKIES.get('device_id')
        if not device_id:
            return JsonResponse({'message': 'Device ID not found.'}, status=400)
        wishlist, created = Wishlist.objects.get_or_create(product=product,  device=device_id)
    else:
        wishlist, created = Wishlist.objects.get_or_create(product=product, user=user)
    wishlist.save()

    return redirect('wishlist')






def remove_from_wishlist(request, wishlist_item_id):
    try:
        if request.user.is_authenticated:
            wishlist_item = Wishlist.objects.get(id=wishlist_item_id, user=request.user)
        else:
            wishlist_item = Wishlist.objects.get(id=wishlist_item_id)
        wishlist_item.delete()
    except Wishlist.DoesNotExist:
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

    return redirect('customer_order')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            customer = Customer.objects.get(email=email)
           
            if customer.email == email:
            
                message = generate_otp()
                sender_email = "plantorium1@gmail.com"
                receiver_mail = email
                password = "lhfkxofxdfyhflkq"

                try:
                    with smtplib.SMTP("smtp.gmail.com", 587) as server:
                        server.starttls()
                        server.login(sender_email, password)
                        server.sendmail(sender_email, receiver_mail, message)

                except smtplib.SMTPAuthenticationError:
                    messages.error(request, 'Failed to send OTP email. Please check your email configuration.')
                    return redirect('signup')
                
                request.session['email'] =  email
                request.session['otp']   =  message
                messages.success (request, 'OTP is sent to your email')
                return redirect('reset_password')   
            
        except Customer.DoesNotExist:
            messages.info(request,"Email is not valid")
            return redirect('login')
    else:
        return redirect('login')

def generate_otp(length = 6):
    return ''.join(secrets.choice("0123456789") for i in range(length)) 

def reset_password(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        stored_otp = request.session.get('otp')
        if entered_otp == stored_otp:
            if new_password == confirm_password:
                email = request.session.get('email')
                try:
                    customer = Customer.objects.get(email=email)
                    customer.set_password(new_password)
                    customer.save()
                    del request.session['email'] 
                    del request.session['otp']
                    messages.success(request, 'Password reset successful. Please login with your new password.')
                    return redirect('login')
                except Customer.DoesNotExist:
                    messages.error(request, 'Failed to reset password. Please try again later.')
                    return redirect('login')
            else:
                messages.error(request, 'New password and confirm password do not match.')
                return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please enter the correct OTP.')
            return redirect('reset_password')
    else:
        return render(request, 'passwordreset.html')


def search(request):
    if 'email' in request.session:
        query = request.GET.get('q')
    
        if query:
            results = Product.objects.filter(product_name__icontains = query)
        
        else:
            results = []
        

        paginator = Paginator(results, 10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj' :  page_obj,
            'query'    :  query,
            
        }
        
        return render(request,'userproduct.html',context)
    return redirect('login')


    
def changepassword(request):
    if request.method == 'POST':
        old_password = request.POST.get('old')
        new_password = request.POST.get('new_password1')
        confirm_password = request.POST.get('new_password2')

        customer = Customer.objects.get(username=request.user.username)

        if customer.check_password(old_password):
            if new_password == confirm_password:
                customer.set_password(new_password)
                customer.save()
                messages.success(request, 'Password changed successfully.')
                return redirect('home')
            else:
                messages.error(request, 'New password and confirm password do not match.')
                return redirect ('edit_profile')
        else:
            messages.error(request, 'Old password is incorrect.')
            return redirect('edit_profile')

    return render(request, 'testing.html')


def shippingaddress(request):

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
       
       

        if not email or not first_name or not last_name or not number or not address1 or not address2 or not country or not state or not city or not zip :
            messages.error(request, 'Please input all the details!!!')
            return redirect('edit_profile')
        
        user = request.user

        address = Address.objects.create(
            user         =    user,
            first_name   =    first_name,
            last_name    =    last_name,
            email        =    email,
            number       =    number,
            address1     =    address1,
            address2     =    address2,
            country      =    country,
            state        =    state,
            city         =    city,
            zip_code     =    zip_code
        )
        address.save()
        return redirect('edit_profile')
        
    else:
        return render(request, 'testing.html')


def customer_order(request):
    if 'email' in request.session:
        user = request.user 
        orders = Order.objects.filter(user = user).order_by('-id')
        context ={
            'orders':orders,
        }
        return render(request,'customer_order.html',context)
    else:
        return redirect('home')

            
            

def proceedtopay(request):
    cart = Cart.objects.filter(user=request.user)
    total = 0
    shipping = 10
    subtotal=0
    for cart_item in cart:
        
        if cart_item.product.category.category_offer:   
            itemprice2=(cart_item.product.price - cart_item.product.category.category_offer)*(cart_item.quantity)
            subtotal=subtotal+itemprice2
            
        elif cart_item.product.product_offer:
            itemprice2 = (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer/100)) * cart_item.quantity
            subtotal=subtotal+itemprice2

        else:
            
            itemprice=(cart_item.product.price)*(cart_item.quantity)
            
            subtotal=subtotal+itemprice
    for item in cart:
       
    
        discount = request.session.get('discount', 0)
    total=subtotal+shipping 
    if discount:
        total -= discount 
        

    
        

    return JsonResponse({
        'total' : total

    })


def razorpay(request,address_id):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    
  
    subtotal=0
    for cart_item in cart_items:
        
        if cart_item.product.category.category_offer:
            
            itemprice2=(cart_item.product.price - cart_item.product.category.category_offer)*(cart_item.quantity)
            subtotal=subtotal+itemprice2
        elif cart_item.product.product_offer:
            itemprice2 =  (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer/100)) * cart_item.quantity
            subtotal=subtotal+itemprice2     
        else:
            
            itemprice=(cart_item.product.price)*(cart_item.quantity)
            
            subtotal=subtotal+itemprice
    shipping_cost = 10 
    total = subtotal + shipping_cost if subtotal else 0
    
    discount = request.session.get('discount', 0)
    
    if discount:
        total -= discount 

   
   

    payment  =  'razorpay'
    user     = request.user
    cart_items = Cart.objects.filter(user=user)
    address = Address.objects.get(id=address_id)

    
    order = Order.objects.create(
        user          =     user,
        address       =     address,
        amount        =     total,
        payment_type  =     payment,
    )

    for cart_item in cart_items:
        product = cart_item.product
        product.stock -= cart_item.quantity
        product.save()

        order_item = OrderItem.objects.create(
            order         =     order,
            product       =     cart_item.product,
            quantity      =     cart_item.quantity,
            image         =     cart_item.product.image  
        )
    
    cart_items.delete()
    return redirect('success')


@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def coupon(request):
    if 'admin' in request.session:
        coupons = Coupon.objects.all().order_by('id')
        context = {'coupons': coupons}
        return render(request, 'coupon.html', context)
    else:
        return redirect('admin')


def addcoupon(request):
    if request.method == 'POST':
        coupon_code    = request.POST.get('Couponcode')
        discount_price  = request.POST.get('dprice')
        minimum_amount = request.POST.get('amount')
        
        coupon = Coupon(coupon_code=coupon_code, discount_price=discount_price, minimum_amount=minimum_amount)
        coupon.save()

        return redirect('coupon')
    

def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')

        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code)
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code')
            return redirect('checkout')

        user = request.user
        cart_items = Cart.objects.filter(user=user)
        subtotal = 0
        shipping_cost = 10
        total_dict = {}
        coupons = Coupon.objects.all()

        for cart_item in cart_items:
            if cart_item.quantity > cart_item.product.stock:
                messages.warning(request, f"{cart_item.product.product_name} is out of stock.")
                cart_item.quantity = cart_item.product.stock
                cart_item.save()

            if cart_item.product.category.category_offer:
                item_price = (cart_item.product.price - cart_item.product.category.category_offer) * (cart_item.quantity)
                total_dict[cart_item.id] = item_price
                subtotal += item_price

            elif cart_item.product.product_offer:
                item_price = (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer / 100)) * cart_item.quantity
                total_dict[cart_item.id] = item_price
                subtotal += item_price

            else:
                item_price = cart_item.product.price * cart_item.quantity
                total_dict[cart_item.id] = item_price
                subtotal += item_price

        if subtotal >= coupon.minimum_amount:
            messages.success(request, 'Coupon applied successfully')
            request.session['discount'] = coupon.discount_price
            total = subtotal - coupon.discount_price + shipping_cost
        else:
            messages.error(request, 'Coupon not available for this price')
            total = subtotal + shipping_cost

        for cart_item in cart_items:
            cart_item.total_price = total_dict.get(cart_item.id, 0)
            cart_item.save()

        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'total': total,
            'coupons': coupons,
            'discount_amount': coupon.discount_price,
        }

        return render(request, 'cart.html', context)

    return redirect('cart')
 
@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)   
def searchcategory(request):
    if 'admin' in request.session:
        query = request.GET.get('q')

        if query:
            results = Category.objects.filter( category_name__icontains = query)

        else:
            results = []

        paginator = Paginator(results, 10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'categories' :  page_obj,
            'query'    :  query,
            
        }
        
        return render(request,'category.html',context)

    else:
        return redirect('admin')


@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def searchproduct(request):
    if 'admin' in request.session:
        query = request.GET.get('q')

        if query:
            results = Product.objects.filter( product_name__icontains = query )

        else:
            results = []

        paginator = Paginator(results, per_page=3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
            
        context = {
            'page_obj': page_obj,
            'query'    :  query,
        }
        return render(request, 'products.html', context)
    else:
        return redirect ('admin')



def edit_address(request, address_id):
    try:
        address = Address.objects.get(id=address_id)
    except Address.DoesNotExist:
        messages.error(request, 'Address not found')
        return redirect('edit_profile')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        number = request.POST.get('number')
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        country = request.POST.get('country')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')

        address.first_name = first_name
        address.last_name = last_name
        address.email = email
        address.number = number
        address.address1 = address1
        address.address2 = address2
        address.country = country
        address.city = city
        address.state = state
        address.zip_code = zip_code
        address.save()
        messages.success(request, 'Address updated successfully')

    return redirect('edit_profile')



def delete_address(request, address_id):
    try:
        address = Address.objects.get(id=address_id)
    except Address.DoesNotExist:
        return redirect('edit_profile')

    address.delete()

    messages.success(request, 'Address deleted successfully.')
    return redirect('edit_profile')



def admin_order_details(request,order_id):
    order = get_object_or_404(Order, id=order_id)

    context = {
        'order': order,
        
    }

    return render(request, 'admin_order_details.html', context)