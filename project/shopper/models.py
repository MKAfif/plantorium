from django.db import models
from app1.models import Product,Customer
from datetime import date


class Cart(models.Model):
    user           =     models.ForeignKey(Customer, on_delete=models.CASCADE,null=True,blank=True)
    product        =     models.ForeignKey(Product,on_delete=models.CASCADE,null=True,blank=True)
    quantity       =     models.IntegerField(default=0)
    image          =     models.ImageField(upload_to='products',null=True, blank=True )
    device              = models.CharField(max_length=255, null=True, blank=True)

    @property
    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
          return f"Cart: {self.user.username} - {self.product} - Quantity: {self.quantity}"



class Wishlist(models.Model):
    user          =     models.ForeignKey(Customer,on_delete=models.CASCADE,null = True,blank=True)
    product       =     models.ForeignKey(Product,on_delete=models.CASCADE)
    image         =     models.ImageField(upload_to='products',null = True,blank=True)
    device              = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Wishlist:{self.user.username}-{self.product}"
     
class Address(models.Model):
    user           =     models.ForeignKey(Customer,on_delete=models.CASCADE)
    first_name     =     models.CharField(max_length=50,null=False,blank=True)
    last_name      =     models.CharField(max_length=50,null=False,blank=True)
    email          =     models.EmailField()
    number         =     models.CharField(max_length=10)
    address1       =     models.CharField(max_length=200)
    address2       =     models.CharField(max_length=200)
    country        =     models.CharField(max_length=15)
    state          =     models.CharField(max_length=15)
    city           =     models.CharField(max_length=15)
    zip_code       =     models.IntegerField()
   
    



    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    


class Coupon(models.Model):
    coupon_code     =  models.CharField(max_length=100)
    expired         =  models.BooleanField(default=False)
    discount_price  =  models.PositiveIntegerField(default=100)
    minimum_amount  =  models.PositiveIntegerField(default=500)
    expiry_date     =  models.DateField(null=True,blank=True)

    def __str__(self):
        return self.coupon_code


class Order(models.Model):

    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing','processing'),
        ('shipped','shipped'),
        ('delivered','delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded','refunded'),
        ('on_hold','on_hold')

    )

    user           =   models.ForeignKey(Customer, on_delete=models.CASCADE) 
    address        =   models.ForeignKey(Address, on_delete=models.CASCADE)
    product        =   models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    amount         =   models.CharField(max_length=100)  
    payment_type   =   models.CharField(max_length=100)  
    status         =   models.CharField(max_length=100, choices=ORDER_STATUS, default='pending' )  
    quantity       =   models.IntegerField(default=0, null=True, blank=True)
    image          =   models.ImageField(upload_to='products', null=True, blank=True)
    date           =   models.DateField(default=date.today)
    coupon         =   models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Order #{self.pk} - {self.product}"

class OrderItem(models.Model):
    order          =   models.ForeignKey(Order,on_delete=models.CASCADE)
    product        =   models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity       =   models.IntegerField(default=1)
    image          =   models.ImageField(upload_to='products', null=True, blank=True)

    def __str__(self):
        return str(self.id)


     
class Images(models.Model):
    product     =  models.ForeignKey(Product, on_delete=models.CASCADE)
    images      =  models.ImageField(upload_to='products')

