from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegistrationForm, RatingForm, CheckOutForm
from . import models
from django.db.models import Q, Max, Min, Avg
from .sslcommerz import generate_sslcommerz_payment

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username= username, password = password)
        if user is not None:
            login(request, user)
            redirect('')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, '')


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration is successful !" )
            return redirect('')
    else: 
        form = RegistrationForm()
    
    return render(request, '', {'form':form})



def logout_view(request):
    logout(request)
    return render('')

def home(request):
    featured_products = models.Product.objects.filter(available=True).order_by('-created_at')[:8]
    categories = models.Category.objects.all()

    context = {
        'featured_products':featured_products,
        'categories':categories,
    }
    return render(request, '', context)


def product_list(request, category_slug = None):
    category = None
    categories = models.Category.object.all()
    products = models.Product.objects.all()

    if category_slug:
        category = get_object_or_404(models.Category, category_slug)
        products = products.filter(category = category)

    min_price = products.aggregate(Min('price'))['price__min'] # For showing the min price in the html (filtering part)
    max_price = products.aggregate(Max('price'))['price__max'] # For showing the max price in the html (filtering part)

    if request.GET.get('min_price'):
        products = products.filter(price__gte= request.GET('min_price')) # gte = Greater then equal

    if request.GET.get('max_price'):
        products = products.filter(price__lte= request.GET('max_price')) # lte = less then equal

    if request.GET.get('rating'):
        products = products.annotate(avg_rating = Avg('ratings__rating')).filter(avg_rating = request.GET.get('rating'))

        """ 1) annotate() is creating a temporary variable name 'avg_rating' for each product and populate those variable with their average ratings.
            2) ratings__rating means:  'related_name'  = 'ratings' to access the 'Rating' Model and its 'rating' field using reverse relationship.
            2) products.annotate(avg_rating = Avg('ratings__rating')) this part is calculating the average of all related ratings for each product. 
            3) filter(avg_rating = request.GET.get('rating')) this part is taking frontend filter info. with request.GET.get('rating')
                And keeping only products matching the desired rating (using filter method). 
        """
    if request.GET.get('search'):
        query = request.GET.get('search')
        products = products.filter(
            Q(name__icontains = query)|
            Q(description__icontains = query)|
            Q(category_name__icontains = query)
        )
        context = {
            'products':products,
            'category':category,
            'categories':categories,
            'min_price':min_price,
            'max_price':max_price,
        }
    return render(request, '', context)



def products_details(request, slug):
    product = get_object_or_404(models.Product, slug = slug , available = True)
    related_products = models.Product.objects.filter(category = product.category).exclude(id= product.id)

    user_rating = None

    if request.user.is_authenticated:
        try:
            user_rating = models.Rating.objects.get(product= product, user= request.user)
        except models.Rating.DoesNotExist:
            pass

    rating_form = RatingForm(instance=user_rating)

    context = {
        'product': product,
        'related_products': related_products,
        'user_rating': user_rating,
        'rating_form': rating_form,
    }

    return render(request, '', context)



def rate_product(request, product_id):
    product = get_object_or_404(models.Product, id= product_id)
    order_items = models.OrderItem.objects.filter(
        order__user = request.user,
        product = product,
        order__paid = True,
    )

    if not order_items.exists():
        messages.warning(request, 'You can only rate products you have purchased!') 
        return redirect('')
    
    try:
        rating = models.Rating.objects.get(product=product, user = request.user )
    except models.Rating.DoesNotExist:
        rating = None
    
    if request.method == 'POST':
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.product = product
            rating.user = request.user
            form.save()
            return redirect('')
    else:
        form = RatingForm(instance=rating)

    return render(request, '', {'form':form,'product':product})



def cart_add(request, product_id):
    product = get_object_or_404(models.Product, id= product_id)
    
    # Checking User have any existing cart
    try:
        # if the user already have a cart , then get the cart 
        cart = models.Cart.objects.get(user = request.user)
    except models.Cart.DoesNotExist:
        # if the user doesn't have any cart, then create new one for that user
        cart = models.Cart.objects.create(user = request.user)

    # Add an item in the cart
    try: 
        # the item is already exist in the cart -> increase the quantity
        cart_item = models.CartItem.objects.get(cart = cart, product = product)
        cart_item.quantity += 1
        cart_item.save()
    except models.CartItem.DoesNotExist:
        # the item didn't exist in the cart -> create or add the item to the cart, and make initial quantity one
        models.CartItem.objects.create(product= product, cart= cart, quantity= 1)
    
    messages.success(request, f"{product.name} has been added to your cart!")
    return render(request, '')



# cart update : cart item increase or decrease
def cart_update(request, product_id):
    cart = get_object_or_404(models.Cart, user= request.user)
    product = get_object_or_404(models.Product, id= product_id)
    cart_item = get_object_or_404(models.CartItem,cart=cart, product= product)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart_item.delete()
        messages.success(request,f"{product.name} has been deleted from your cart!")
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request,"Cart updated successfully!")



def cart_remove(request, product_id):
    cart = get_object_or_404(models.Cart, user= request.user)
    product = get_object_or_404(models.Product, id= product_id)
    cart_item= get_object_or_404(models.CartItem, cart=cart, product=product)
    cart_item.delete()
    messages.success(request,f"{product.name} has been deleted from your cart!")
    return redirect('')



def cart_details(request):
    try:
        # user has a cart
        cart = models.Cart.objects.get(user = request.user)
    except models.Cart.DoesNotExist:
        # user has no cart
        cart = models.Cart.objects.create(user = request.user)

    return render(request, '', {'cart':cart})


def checkout(request):
    try:
        cart = models.Cart.objects.get(user= request.user)
        if not cart.items.exists():
            messages.warning(request, 'Your cart is empty')
            return redirect('')
    except models.Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty')
        return redirect('')

    # After clicking checkout btn, have to full up checkout form (in this case cart is not empty)
    if request.method == 'POST':
        form = CheckOutForm(request.POST)
        if form.is_valid():
            order = form.save(commit= False)
            order.user = request.user
            order.save()

            # product -> cart Item -> order item 
            for item in cart.items.all():
                models.OrderItem.objects.create(
                    order = order,
                    product = item.product,
                    price = item.price,
                    quantity = item.quantity,
                )
            # After oder done, cart will be deleted (i.e. the previous items added to the cart, will be gone from the cart after order)
            cart.items.all().delete()
            request.session['order_id']= order.id
            return redirect('')
    else:
        form = CheckOutForm()
    
    return render(request, '', {
        'cart': cart,
        'form': form,
    })

# Payment process
def payment_process(request):
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('')
    
    order = get_object_or_404(models.Order, id= order_id)
    payment_data = generate_sslcommerz_payment(request, order)

    if payment_data['status'] == 'SUCCESS':
        return redirect('')
    else:
        messages.error(request, 'Payment gateway error')
        return redirect('')
    



# Payment Success
def payment_success(request, order_id):
    order = get_object_or_404(models.Order, id= order_id, user= request.user)
    
    order.paid = True
    order.status = 'processing'
    order.transaction_id = order.id
    order.save()

    order_items = order.order_items.all()
    for item in order_items:
        product = item.product
        product.stock -= item.quantity 

        if product.stock < 0:
            product.stock = 0
        product.save()

    messages.success(request,"Payment Successful" )    
    return render(request, '', {'order': order})



# Payment Fail
def payment_fail(request, order_id):
    order = get_object_or_404(models.Order, id= order_id, user= request.user)
    order.status = 'canceled'
    order.save()
    return redirect('')



# Payment Cancel
def payment_cancel(request, order_id):
    order = get_object_or_404(models.Order, id= order_id, user= request.user)
    order.status = 'canceled'
    order.save()
    return redirect('')
