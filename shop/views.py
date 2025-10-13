from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegistrationForm, RatingForm, CheckOutForm
from . import models
from django.db.models import Q, Max, Min, Avg

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
            login(request, login)
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

