from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager




class Customer(AbstractUser):
    username           =   models.CharField(unique=True,null=False,blank=True)
    email              =   models.EmailField(unique=True)
    number             =   models.CharField(max_length=10)
    is_verified        =   models.BooleanField(default=False)
    email_token        =   models.CharField(max_length=100, null=True, blank=True)
    forgot_password    =   models.CharField(max_length=100,null=True, blank=True)
    last_login_time    =   models.DateTimeField(null = True, blank = True)
    last_logout_time   =   models.DateTimeField(null=True,blank=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=[]

    def __str__(self):
        return self.email
    




class Category(models.Model):
    category_name  =   models.CharField(max_length=100)
    description    =   models.CharField(max_length=200,default='')
    image          =   models.ImageField(upload_to='products')
 
    


class Product(models.Model):
   
    product_name   =     models.CharField(max_length=100)
    description    =     models.CharField(max_length=200,default='')
    category       =     models.ForeignKey(Category, on_delete=models.CASCADE)
    price          =     models.IntegerField(default=0)
    image          =     models.ImageField(upload_to='products')
