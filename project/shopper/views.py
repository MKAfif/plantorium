
from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from .models import Cart,Product,Customer,Order,Address,Wishlist,Coupon
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



@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def cart(request):
    if 'email' in request.session:
        if 'discount' in request.session:
            del request.session['discount']

        user = request.user
        cart_items = Cart.objects.filter(user=user)

        for cart_item in cart_items:
            if cart_item.quantity > cart_item.product.stock:
                messages.warning(request, f"{cart_item.product. product_name} is out of stock.")
                cart_item.quantity = cart_item.product.stock
                cart_item.save()
        
        cart_items = cart_items.annotate(item_total=F('quantity') * F('product__price'))
        
        subtotal   = cart_items.aggregate(subtotal=Sum('item_total'))['subtotal']
        
        for cart_item in cart_items:
            cart_item.total_price = cart_item.item_total
            cart_item.save()
        shipping_cost = 10 
        
        total = subtotal + shipping_cost if subtotal else 0
        coupons = Coupon.objects.all()
        context = {
            'cart_items': cart_items,
            'subtotal'  : subtotal,
            'total'     : total,
            'coupons'   : coupons
        }
        
        
        return render(request, 'cart.html', context)
    
    else:
          return redirect('login')


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
    if 'email' in request.session:
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        cart_items = cart_items.annotate(item_total=F('quantity') * F('product__price'))
        subtotal = cart_items.aggregate(subtotal=Sum('item_total'))['subtotal']
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
        
            
        }
        return render(request, 'checkout.html', context)
    else:
        return redirect ('login')

    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def productdetails(request ,product_id=None ):
    if 'email' in request.session:
        context ={}
        try:
            context['product'] = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise Http404("Product doesnot exst")
    
        return render(request, 'detail.html',context)
    else:
        return redirect('login')    

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
    
    cart_items = cart_items.annotate(item_total=F('quantity') * F('product__price'))
    
    subtotal = cart_items.aggregate(subtotal=Sum('item_total'))['subtotal']

    shipping_cost = 10 
    
    total = subtotal + shipping_cost if subtotal else 0
    
    if request.method == 'POST':
        payment       =    request.POST.get('payment')
        select        =    request.POST.get('addressId')
       
       

        if not payment or not select:
            messages.error(request, 'Please fill all the fields!!!')
            return redirect('checkout')
       
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        address = Address.objects.get(id=request.POST.get('addressId'))
        
        for cart_item in cart_items:
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()

            order = Order.objects.create(

                user          =     user,
                address       =     address,
                product       =     cart_item.product,
                amount        =     total,
                payment_type  =     payment,
                quantity      =     cart_item.quantity,
                image         =     cart_item.product.image  
            )

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


 
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache     
def order(request):
    if 'admin' in request.session:
        orders = Order.objects.all().order_by('id')
        
       
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
    if 'email' in request.session:
        user = request.user
        wishlist_items = Wishlist.objects.filter(user=user)

        context = {
            'wishlist_items': wishlist_items
        }

        return render(request, 'wishlist.html', context)
    else:
         return redirect('login')



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
    user = request.user 
    orders = Order.objects.filter(user = user)
    context ={
        'orders':orders
    }
    return render(request,'customer_order.html',context)

            
            

def proceedtopay(request):
    cart = Cart.objects.filter(user=request.user)
    total = 0
    shipping = 10
    for item in cart:
        total = total + item.product.price * item.quantity 
        discount = request.session.get('discount', 0)
    total=total+shipping 
    if discount:
        total -= discount 
        print("After applying coupon:", total)

    
        

    return JsonResponse({
        'total' : total

    })


def razorpay(request,address_id):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    
    cart_items = cart_items.annotate(item_total=F('quantity') * F('product__price'))
    
    subtotal = cart_items.aggregate(subtotal=Sum('item_total'))['subtotal']
   
    shipping_cost = 10 
    
    total = subtotal + shipping_cost if subtotal else 0
    discount = request.session.get('discount', 0)
    
    if discount:
        total -= discount 

   
   

    payment  =  'razorpay'
    user     = request.user
    cart_items = Cart.objects.filter(user=user)
    address = Address.objects.get(id=address_id)

    
    for cart_item in cart_items:
        order = Order(
            user          =     user,
            address       =     address,
            product       =     cart_item.product,
            amount        =     total,
            payment_type  =     payment,
            quantity      =     cart_item.quantity,
            image         =     cart_item.product.image  
        )
        order.save()
        
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
        cart_items = cart_items.annotate(item_total=F('quantity') * F('product__price'))
        subtotal = cart_items.aggregate(subtotal=Sum('item_total'))['subtotal']

        coupons = Coupon.objects.all()

       
       

        if subtotal is None:
            subtotal = 0

        if subtotal >= coupon.minimum_amount:
            messages.success(request, 'Coupon applied successfully')
            request.session['discount'] = coupon.discount_price
        else:
            messages.error(request, 'Coupon not availabe for this price')
          
           
        shipping_cost = 10
        total = subtotal - coupon.discount_price + shipping_cost
        

        for cart_item in cart_items:
            if cart_item.quantity > cart_item.product.stock:
                messages.warning(request, f"{cart_item.product.product_name} is out of stock !!!")
                cart_item.quantity = cart_item.product.stock
                cart_item.save()


        context = {
            'cart_items'      :  cart_items,
            'subtotal'        :  subtotal,
            'total'           :  total,
            'coupons'         :  coupons,
            'discount_amount' :  coupon.discount_price,
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



