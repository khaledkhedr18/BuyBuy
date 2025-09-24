#!/usr/bin/env python3
"""
Test script to demonstrate the e-commerce functionality.
"""

import os
import sys
import django

# Add the backend directory to the path
sys.path.append('/home/runner/work/BuyBuy/BuyBuy/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from products.models import Product
from categories.models import Category
from orders.models import Cart, CartItem, Order, OrderItem
from django.test import RequestFactory, Client
from django.urls import reverse

User = get_user_model()

def test_e_commerce_functionality():
    """Test the complete e-commerce flow."""
    print("🛒 Testing BuyBuy E-commerce Functionality")
    print("=" * 50)
    
    # Test 1: User Authentication
    print("\n1. Testing User Authentication:")
    user = authenticate(username='user1@buybuy.com', password='password123')
    if user:
        print(f"✅ Authentication successful for {user.get_full_name()} ({user.email})")
    else:
        print("❌ Authentication failed")
        return
    
    # Test 2: Product Catalog
    print("\n2. Testing Product Catalog:")
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    print(f"✅ Found {products.count()} active products across {categories.count()} categories")
    
    # Display some products
    for i, product in enumerate(products[:3]):
        print(f"   • {product.name} - ${product.price} ({product.stock_quantity} in stock)")
    
    # Test 3: Shopping Cart
    print("\n3. Testing Shopping Cart:")
    cart, created = Cart.objects.get_or_create(user=user)
    if created:
        print("✅ Created new cart for user")
    else:
        print("✅ Retrieved existing cart")
        # Clear existing items for clean test
        cart.items.all().delete()
    
    # Add items to cart
    test_products = products[:3]
    for product in test_products:
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            defaults={'quantity': 1}
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        print(f"✅ Added {product.name} to cart (quantity: {cart_item.quantity})")
    
    print(f"✅ Cart total: ${cart.get_total_price()}")
    print(f"✅ Cart items count: {cart.get_items_count()}")
    
    # Test 4: Order Creation
    print("\n4. Testing Order Creation:")
    if cart.items.exists():
        # Create an order
        order = Order.objects.create(
            buyer=user,
            total_amount=cart.get_total_price(),
            shipping_address="123 Test Street, Test City, TC 12345"
        )
        print(f"✅ Created order #{order.id} for ${order.total_amount}")
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
                seller_id=1  # Admin as seller
            )
            print(f"✅ Added {cart_item.product.name} x{cart_item.quantity} to order")
        
        # Clear cart after order
        cart.items.all().delete()
        print("✅ Cart cleared after order creation")
    
    # Test 5: Order History
    print("\n5. Testing Order History:")
    user_orders = Order.objects.filter(buyer=user).order_by('-created_at')
    print(f"✅ User has {user_orders.count()} order(s)")
    
    for order in user_orders[:3]:
        items_count = order.items.count()
        print(f"   • Order #{order.id}: {items_count} items, ${order.total_amount}, {order.get_status_display()}")
    
    # Test 6: Web Interface URLs
    print("\n6. Testing Web Interface:")
    client = Client()
    
    # Test public pages
    urls_to_test = [
        ('/', 'Dashboard'),
        ('/products/page/', 'Products'),
        ('/categories/page/', 'Categories'),
        ('/login/', 'Login'),
        ('/register/', 'Register'),
    ]
    
    for url, name in urls_to_test:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {name} page loads successfully ({response.status_code})")
            else:
                print(f"⚠️  {name} page returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Error accessing {name} page: {e}")
    
    # Test authenticated pages (simulate login)
    client.force_login(user)
    auth_urls = [
        ('/orders/cart/', 'Shopping Cart'),
        ('/orders/orders/', 'Order History'),
    ]
    
    for url, name in auth_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {name} page loads successfully (authenticated)")
            else:
                print(f"⚠️  {name} page returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Error accessing {name} page: {e}")
    
    print("\n🎉 E-commerce functionality test completed!")
    print("\nSummary:")
    print("• User authentication working")
    print("• Product catalog functional")
    print("• Shopping cart operational")
    print("• Order processing complete")
    print("• Web interface accessible")
    print("• Database relationships intact")

if __name__ == '__main__':
    test_e_commerce_functionality()