"""
Product views for the BuyBuy e-commerce backend.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Product, Cart, CartItem, Order, OrderItem
from .serializers import ProductSerializer, ProductListSerializer
from categories.models import Category

@login_required
def product_list_view(request):
    """Display all products."""
    products = Product.objects.filter(is_active=True).select_related('category', 'seller')
    return render(request, 'products.html', {'products': products})

@login_required
def product_detail_view(request, pk):
    """Display product details."""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, 'product_detail.html', {'product': product})

@login_required
def category_products_view(request, category_id):
    """Display products in a specific category."""
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).select_related('category', 'seller')
    return render(request, 'category_products.html', {
        'category': category,
        'products': products
    })

@login_required
def my_products_view(request):
    """Display user's products for sale."""
    products = Product.objects.filter(seller=request.user)
    return render(request, 'my_products.html', {'products': products})

@login_required
def add_product_view(request):
    """Add new product for sale."""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock_quantity = request.POST.get('stock_quantity')
        category_id = request.POST.get('category')
        image_url = request.POST.get('image_url')

        try:
            from categories.models import Category
            category = Category.objects.get(id=category_id)

            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                stock_quantity=stock_quantity,
                category=category,
                seller=request.user,
                image_url=image_url
            )

            messages.success(request, 'Product added successfully!')
            return redirect('products:my_products')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')

    from categories.models import Category
    categories = Category.objects.filter(is_active=True)
    return render(request, 'add_product.html', {'categories': categories})

@login_required
def add_to_cart_view(request, pk):
    """Add product to cart."""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    quantity = int(request.POST.get('quantity', 1))

    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    messages.success(request, f'{product.name} added to cart!')
    return redirect('products:product_list')

@login_required
def cart_view(request):
    """Display user's cart."""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product')
        cart_total = cart.total_price
    except Cart.DoesNotExist:
        cart = None
        cart_items = []
        cart_total = 0

    return render(request, 'cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total': cart_total
    })

@login_required
def remove_from_cart_view(request, pk):
    """Remove item from cart."""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(cart=cart, id=pk)
        cart_item.delete()
        messages.success(request, 'Item removed from cart!')
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        messages.error(request, 'Item not found in cart!')

    return redirect('products:cart')

@login_required
def update_cart_item_view(request, pk):
    """Update cart item quantity."""
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, id=pk)

            new_quantity = int(request.POST.get('quantity', 1))
            if new_quantity <= 0:
                cart_item.delete()
                messages.success(request, 'Item removed from cart!')
            else:
                cart_item.quantity = new_quantity
                cart_item.save()
                messages.success(request, 'Cart updated successfully!')

        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            messages.error(request, 'Item not found in cart!')
        except ValueError:
            messages.error(request, 'Invalid quantity!')

    return redirect('products:cart')

@login_required
def checkout_view(request):
    """Checkout process."""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product')

        if not cart_items.exists():
            messages.error(request, 'Your cart is empty!')
            return redirect('products:cart')

        if request.method == 'POST':
            shipping_address = request.POST.get('shipping_address')

            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    buyer=request.user,
                    total_amount=cart.total_price,
                    shipping_address=shipping_address
                )

                # Create order items
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        seller=cart_item.product.seller,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )

                    # Update stock
                    product = cart_item.product
                    product.stock_quantity -= cart_item.quantity
                    product.save()

                # Clear cart
                cart_items.delete()

                messages.success(request, f'Order #{order.id} placed successfully!')
                return redirect('products:order_detail', pk=order.id)

        return render(request, 'checkout.html', {
            'cart': cart,
            'cart_items': cart_items
        })

    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty!')
        return redirect('products:cart')

@login_required
def my_orders_view(request):
    """Display user's orders."""
    orders = Order.objects.filter(buyer=request.user).prefetch_related('items__product')
    return render(request, 'my_orders.html', {'orders': orders})

@login_required
def order_detail_view(request, pk):
    """Display order details."""
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    return render(request, 'order_detail.html', {'order': order})

@login_required
def my_sales_view(request):
    """Display user's sales."""
    sales = OrderItem.objects.filter(seller=request.user).select_related(
        'order', 'product', 'order__buyer'
    ).order_by('-created_at')
    return render(request, 'my_sales.html', {'sales': sales})
