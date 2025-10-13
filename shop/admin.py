from django.contrib import admin
from .models import Category, Product, Rating, Cart, CartItem, Order, OrderItem
# Register your models here.

# admin.site.register(Category)
# admin.site.register(Product)
# admin.site.register(Rating)
# admin.site.register(Cart)
# admin.site.register(CartItem)
# admin.site.register(Order)
# admin.site.register(OrderItem)



# INLINE CLASSES 

class RatingInline(admin.TabularInline):
    model = Rating
    extra = 1
    readonly_fields = ('user', 'created_at')
    show_change_link = True


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    show_change_link = True


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('price',)
    show_change_link = True


# CATEGORY ADMIN 

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


# PRODUCT ADMIN

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'available', 'created_at', 'updated_at')
    list_filter = ('available', 'category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'stock', 'available')
    inlines = [RatingInline]


# RATING ADMIN

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')


# CART ADMIN 

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'get_total_price')
    search_fields = ('user__username',)
    inlines = [CartItemInline]


# CART ITEM ADMIN 

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'get_cost')
    search_fields = ('cart__user__username', 'product__name')

    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = 'Total Cost'


# ORDER ADMIN 

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'email','status', 'paid', 'created_at', 'updated_at')
    list_filter = ('status', 'paid', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'user__username')
    list_editable = ('status', 'paid')
    inlines = [OrderItemInline]


# ORDER ITEM ADMIN 

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'get_cost')
    search_fields = ('order__user__username', 'product__name')

    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = 'Total Cost'
