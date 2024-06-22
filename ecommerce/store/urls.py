from django.urls import path

from . import views


urlpatterns = [
	#Leave as empty string for base url
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
    path('store/', views.store_view, name='store'),
    path('checkout/', views.checkout, name='checkout'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),


    path('', views.store, name='store'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('about-us/', views.about_us, name='about_us'),

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
    path('payment/', views.payment_view, name='payment_view'),
    path('payment_success/', views.payment_success, name='payment_success'),

]
   