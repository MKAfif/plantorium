from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control,never_cache
from .models import Customer,Product,Category
from django.contrib import messages,auth
import secrets
import smtplib
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist



# @login_required(login_url='login')
@never_cache
def loginPage(request):
    context = {
        'messages': messages.get_messages(request)
    }
    if 'email' in request.session:
        return redirect('home')
    elif 'admin' in request.session:
        return redirect('admin')
    else:
        if request.method == 'POST':
            email     =  request.POST.get('email')
            password  =  request.POST.get('pass')
            user      =  authenticate( request,email = email, password = password )
        
            if user is not None:
                request.session['email'] = email
                login(request,user)
                return redirect('home')
            else:
               messages.error(request,"username or password is not same")
               return render(request, 'login.html') 
        else:
            return render (request,'login.html',context)


@never_cache
def signupPage(request):
    if 'email' in request.session:
        return redirect('home')

    if request.method == 'POST':
        email     =    request.POST.get('email')
        number    =    request.POST.get('number')
        username  =    request.POST.get('username')
        pass1     =    request.POST.get('password1')
        pass2     =    request.POST.get('password2')

        if not email or not username or not pass1 or not pass2:
            messages.error(request, 'Please input all the details.')
            return redirect('signup')

        if pass1 != pass2:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')

        if not validate_email(email):
            messages.error(request, 'Please enter a valid email address.')
            return redirect('signup')

        if Customer.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('signup')

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

        user = Customer.objects.create_user(username=username, password=pass1, email=email,number=number)
        user.save()
        request.session['email'] =  email
        request.session['otp']   =  message
        messages.success (request, 'OTP is sent to your email')
        return redirect('verify_signup')

    return render(request, 'signup.html')

def generate_otp(length = 6):
    return ''.join(secrets.choice("0123456789") for i in range(length)) 

def validate_email(email):
    return '@' in email and '.' in email
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def verify_signup(request):
    context = {
        'messages': messages.get_messages(request)
    }
    if request.method == "POST":
        
        user  =  Customer.objects.get(email=request.session['email'])
        x     =  request.session.get('otp')
        OTP   =  request.POST['otp']
    
        if OTP == x:
            user.is_verified = True
            user.save()
            del request.session['email'] 
            del request.session['otp']
            
            auth.login(request,user)
            messages.success(request, "Signup successful!")

            return redirect('home')
        else:
            user.delete()
            messages.info(request,"invalid otp")
            del request.session['email']
            return redirect('signup')
    return render(request,'verify_otp.html',context)






@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def home(request):
    if 'email' in request.session:
        categories =  Category.objects.all()
        context    =  {
                'categories':categories
            }
        return render(request,'home.html',context)
    else:
        return redirect('login')




@never_cache    
def logoutPage(request):
    if 'email' in request.session:
        request.session.flush()
    logout(request)
    return redirect('login')

    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def admin_login(request):
    if 'username' in request.session:
        return redirect('home')
    elif 'admin' in request.session:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            username      =  request.POST.get('username')
            pass1         =  request.POST.get('pass')
            user          =  authenticate(request,username=username,password = pass1)

            if user is not None and user.is_superuser:
                login(request,user)
                request.session['admin']=username
                return redirect('dashboard')
            else:
                messages.error(request,"username or password is not same")
                return render(request, 'admin_login.html') 
        else:
             return render (request,'admin_login.html')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def dashboard(request):
    if 'admin' in request.session:
        return render(request,'dashboard.html')
    else:
        return redirect('home')
    
def admin_logout(request):
    if 'admin' in request.session:
        request.session.flush()
    logout(request)
    return redirect('admin')



def customers(request):
    if 'admin' in request.session:    
        customer_list =  Customer.objects.filter(is_staff=False).order_by('id')

        paginator = Paginator(customer_list,2)  

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
        }
        return render(request, 'customer.html', context)
    else:
        return redirect('admin')

      

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def product(request):
    if 'admin' in request.session:
        
        products = Product.objects.all().order_by('id')
               
        paginator = Paginator(products, 3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
           
        }
        return render(request, 'products.html', context)
    else:
        return redirect('admin')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        description = request.POST.get('description')
        category_name = request.POST.get('category')
        category = get_object_or_404(Category, category_name=category_name)  
        price = request.POST.get('price')
        image = request.FILES.get('image')  

        
        if not (product_name and description and category_name and price and image):
            error_message = "Please fill in all the required fields."
            
            categories = Category.objects.all()
            context = {'categories': categories, 'error_message': error_message}
            return render(request, 'add_product.html', context)

        
        
        product = Product()
        product.product_name = product_name
        product.description = description
        product.category = category  
        product.price = price
        product.image = image
        product.save()
        return redirect('products') 

    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'add_product.html', context)

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache    
def userproductpage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            request.session['email']   =  email
            request.session.modified   =  True
            return redirect('userproduct')

    if 'email' in request.session:
        email    =  request.session['email']
        products =  Product.objects.all()
        context  =  {
            'products' :  products,
            'email'    :  email,
        }
        return render(request, 'userproduct.html', context)
    else:
        return redirect('login')
    



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def category(request):
    if 'admin' in request.session:
        categories = Category.objects.all().order_by('id')
        
        
        paginator = Paginator(categories, per_page=3)  # Change the per_page value as desired
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'categories': page_obj,
        }
        return render(request, 'category.html', context)
    else:
        return redirect('admin')
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache          
def add_category(request):
        if request.method  == 'POST':
            category_name  =   request.POST['category_name']
            description    =   request.POST['description']
            image = request.FILES.get('image')
           
            category = Category.objects.create(
                category_name   =  category_name,
                description     =  description,
                image           =  image,
            )
            category.save() 

            return redirect('category')  
        return render(request, 'add_category.html') 



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def editproduct(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
       
        return render(request, 'product_not_found.html')
    
    categories = Category.objects.all()
    context = {
        'product'    : product,
        'categories' : categories,
    }

    return render(request, 'editproduct.html', context)

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def update(request, id):
    product = Product.objects.get(id=id)
    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.description = request.POST.get('description')
        category_name = request.POST.get('category')
        category = Category.objects.get(category_name=category_name)
        product.category = category
        product.price = request.POST.get('price')
        image = request.FILES.get('image')
        if image:
            product.image = image
        product.save()
        return redirect('products') 
    else:
        context = {
            'product': product
        }
    return render(request, 'products.html', context)


    

    


def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return render(request, 'category_not_found.html')

    product.delete()

    return redirect('products')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def editcategory(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return render(request, 'category_not_found.html')

    context = {'category': category}
    return render(request, 'edit_category.html', context)


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def update_category(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return render(request, 'category_not_found.html')

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        if category_name:
            category.category_name = category_name
        category.description = request.POST.get('description')
        image = request.FILES.get('image')
        if image:
            category.image = image
        category.save()
        return redirect('category')

    context = {'category': category}
    return render(request, 'edit_category.html', context)




def delete_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return render(request, 'category_not_found.html')

    category.delete()

    categories = Category.objects.all()
    context = {'categories': categories}

    return redirect('category')


def unblock_customer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except ObjectDoesNotExist:
        return redirect('customer')  
    
    customer.is_active = not customer.is_active
    customer.save()

    return redirect('customer')


def block_customer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return redirect('customer')  
    customer.is_active = False
    customer.save()
    return redirect('customer')
