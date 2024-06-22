from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .models import * 
from .models import Product
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from .forms import PaymentForm, ShippingForm
from .models import Video, Order, OrderItem
from django.conf import settings





def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                # Ensure Customer object exists for the authenticated user
                try:
                    customer = request.user.customer
                except Customer.DoesNotExist:
                    # Create Customer object if it doesn't exist
                    customer = Customer.objects.create(user=user, name=user.username, email=user.email)

                return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create Customer object for the registered user
            customer = Customer.objects.create(user=user, name=user.username, email=user.email)

            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')
      

def store_view(request):
	return render(request, 'store/store.html')

def main_page_view(request):
    return render(request, 'store/main_page.html')

def home(request):
	return render (request, 'store/store/html')

def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)

def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        raise Http404("Product does not exist")
    
    context = {
        'product': product
    }
    return render(request, 'store/product_detail.html', context)

def about_us(request):
      video = Video.objects.last()
      return render(request, 'store/about_us.html', {'video': video})

def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    if request.method == 'POST':
        form = ShippingForm(request.POST)
        if form.is_valid():
            if order.shipping:
                order.address = form.cleaned_data['address']
                order.city = form.cleaned_data['city']
                order.state = form.cleaned_data['state']
                order.zipcode = form.cleaned_data['zipcode']
                order.country = form.cleaned_data['country']
            if request.user.is_anonymous:
                order.name = form.cleaned_data['name']
                order.email = form.cleaned_data['email']
            order.save()
            return redirect('payment.html')  # Redirect to the payment page or handle payment logic here
    else:
        initial_data = {}
        if not request.user.is_anonymous:
            initial_data = {'name': request.user.get_full_name(), 'email': request.user.email}
        form = ShippingForm(initial=initial_data)

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'form': form,
    }
    return render(request, 'store/checkout.html', context)
	


def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)

def payment_view(request):
    if request.method == 'POST':
        # Retrieve data from POST request
        data = json.loads(request.body)
        
        # Process the payment and any other logic here
        # Example: Save payment details to database, send confirmation emails, etc.
        
        # Return a JSON response (optional, based on your needs)
        return JsonResponse({'message': 'Payment processed successfully.'})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

def payment_success(request):
    return render(request, 'store/payment_success.html')
