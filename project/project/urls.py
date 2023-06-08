"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app1 import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include






urlpatterns = [

     path('admin/', admin.site.urls),


#admin login,logout..user signup,login,otp,logout
    
    path('adminn/', views.admin_login,name='admin'),
    path ('admin_logout/',views.admin_logout,name='admin_logout'),
    path('signup/', views.signupPage, name='signup'),
    path('otp/', views.verify_signup, name='otp'),
    path('category/',views.category, name = 'category'),
    path('addc/',views.add_category,name= 'add_category'),
    path('edit/<int:product_id>/',views.editproduct,name='edit_product'),
    path('product/<int:id>/update/', views.update, name='update'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('customer/<int:customer_id>/block/', views.block_customer, name='block_customer'),
    path('customer/<int:customer_id>/unblock/', views.unblock_customer, name='unblock_customer'),
    path('category/<int:id>/update_category/', views.update_category, name='update_category'),
    path('category/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('category/<int:category_id>/edit/', views.editcategory, name='edit_category'),



    
#dashboard,customer,order,product
    path('dashboard/', views.dashboard,name='dashboard'),
    path('Customer/',views.customers,name='customer'),
    path('products/',views.product,name='products'),
    path('add/', views.add_product, name='add_product'),

     


#user side
    path('home/',views.home,name='home'),
    path('', views.loginPage, name='login'),
    path('logout/',views.logoutPage,name='logout'),
    path('userproduct/',views.userproductpage,name='userproduct'),
    path('verify_otp/',views.verify_signup,name='verify_signup'),

# app2
    path('', include('shopper.urls')),

#app3(reportapp)
    path('', include('reportapp.urls')),




]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
