
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static





urlpatterns = [

path('cart/',views.cart,name='cart'),
path('checkout',views.checkout,name='checkout'),
path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
path('productdetail/<int:product_id>',views.productdetails,name='productdetail' ),
path('edit_profile/', views.edit_profile, name='edit_profile'),
path('order/',views.order,name = 'order'),
path('placeorder/',views.placeorder,name='placeorder'),
path('success/',views.success,name='success'),
path('update_order/', views.updateorder, name='update_order'),
path('wishlist/',views.wishlist, name='wishlist'),
path('addtowishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
path('remove_from_wishlist/<int:wishlist_item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
path('forgot-password/', views.forgot_password, name='forgot_password'),
path('reset-password/', views.reset_password, name='reset_password'),






]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
