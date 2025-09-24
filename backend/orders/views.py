"""
Views for order management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Order, OrderItem, Cart, CartItem
from products.models import Product


@login_required
def cart_view(request):
    """Display user's shopping cart."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'orders/cart.html', {'cart': cart})


@login_required
def add_to_cart(request, product_id):
    """Add a product to the shopping cart."""
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('products:products')


@login_required
def remove_from_cart(request, item_id):
    """Remove an item from the shopping cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from cart!')
    return redirect('orders:cart')


@login_required
def checkout(request):
    """Process the checkout."""
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('orders:cart')
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address', '')
        
        with transaction.atomic():
            # Create the order
            order = Order.objects.create(
                buyer=request.user,
                total_amount=cart.get_total_price(),
                shipping_address=shipping_address
            )
            
            # Create order items and reduce stock
            for cart_item in cart.items.all():
                # Check if enough stock is available
                if cart_item.product.stock_quantity < cart_item.quantity:
                    messages.error(request, f'Not enough stock for {cart_item.product.name}')
                    return redirect('orders:cart')
                
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                    seller_id=1  # For now, use admin as seller
                )
                
                # Reduce stock
                cart_item.product.stock_quantity -= cart_item.quantity
                cart_item.product.save()
            
            # Clear the cart
            cart.items.all().delete()
            
            messages.success(request, f'Order #{order.id} placed successfully!')
            return redirect('orders:order_detail', order_id=order.id)
    
    return render(request, 'orders/checkout.html', {'cart': cart})


@login_required
def order_detail(request, order_id):
    """Display order details."""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_list(request):
    """Display user's order history."""
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})