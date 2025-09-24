#!/usr/bin/env python3
"""
Script to populate the BuyBuy database with sample data.
"""

import os
import sys
import django

# Add the backend directory to the path
sys.path.append('/home/runner/work/BuyBuy/BuyBuy/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from categories.models import Category
from products.models import Product

User = get_user_model()

def create_sample_data():
    """Create sample data for the e-commerce site."""
    
    # Create a superuser if it doesn't exist
    admin_user, created = User.objects.get_or_create(
        email='admin@buybuy.com',
        defaults={
            'username': 'admin',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("Created admin user: admin@buybuy.com / admin123")
    
    # Create some regular users
    users = []
    for i in range(3):
        user, created = User.objects.get_or_create(
            email=f'user{i+1}@buybuy.com',
            defaults={
                'username': f'user{i+1}',
                'first_name': f'User{i+1}',
                'last_name': 'TestUser',
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            users.append(user)
            print(f"Created user: user{i+1}@buybuy.com / password123")
    
    # Create categories
    categories_data = [
        {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
        {'name': 'Clothing', 'description': 'Clothing and fashion items'},
        {'name': 'Books', 'description': 'Books and educational materials'},
        {'name': 'Home & Garden', 'description': 'Home and garden products'},
        {'name': 'Sports & Outdoors', 'description': 'Sports and outdoor equipment'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'is_active': True
            }
        )
        categories.append(category)
        if created:
            print(f"Created category: {category.name}")
    
    # Create sample products
    products_data = [
        {
            'name': 'iPhone 15 Pro',
            'description': 'Latest Apple iPhone with advanced camera system',
            'short_description': 'Premium smartphone with A17 Pro chip',
            'sku': 'IPHONE15PRO',
            'price': 999.99,
            'category': categories[0],  # Electronics
            'stock_quantity': 50,
            'seller': admin_user
        },
        {
            'name': 'MacBook Air M3',
            'description': 'Ultralight laptop perfect for productivity and creativity',
            'short_description': 'Lightweight laptop with M3 chip',
            'sku': 'MACBOOK-AIR-M3',
            'price': 1299.99,
            'category': categories[0],  # Electronics
            'stock_quantity': 25,
            'seller': admin_user
        },
        {
            'name': 'Wireless Bluetooth Headphones',
            'description': 'High-quality wireless headphones with noise cancellation',
            'short_description': 'Premium wireless headphones',
            'sku': 'BLUETOOTH-HP-001',
            'price': 199.99,
            'category': categories[0],  # Electronics
            'stock_quantity': 100,
            'seller': admin_user
        },
        {
            'name': 'Classic Cotton T-Shirt',
            'description': 'Comfortable cotton t-shirt in various colors',
            'short_description': '100% cotton comfortable t-shirt',
            'sku': 'TSHIRT-COTTON-001',
            'price': 29.99,
            'category': categories[1],  # Clothing
            'stock_quantity': 200,
            'seller': admin_user
        },
        {
            'name': 'Denim Jeans',
            'description': 'Classic blue denim jeans with perfect fit',
            'short_description': 'Classic blue denim jeans',
            'sku': 'JEANS-DENIM-001',
            'price': 79.99,
            'category': categories[1],  # Clothing
            'stock_quantity': 150,
            'seller': admin_user
        },
        {
            'name': 'Python Programming Guide',
            'description': 'Comprehensive guide to Python programming for beginners',
            'short_description': 'Learn Python programming from scratch',
            'sku': 'BOOK-PYTHON-001',
            'price': 49.99,
            'category': categories[2],  # Books
            'stock_quantity': 75,
            'seller': admin_user
        },
        {
            'name': 'Web Development Masterclass',
            'description': 'Complete guide to modern web development',
            'short_description': 'Master modern web development',
            'sku': 'BOOK-WEBDEV-001',
            'price': 59.99,
            'category': categories[2],  # Books
            'stock_quantity': 50,
            'seller': admin_user
        },
        {
            'name': 'Smart Home Security Camera',
            'description': '1080p HD security camera with mobile app integration',
            'short_description': 'HD security camera for home monitoring',
            'sku': 'CAMERA-SEC-001',
            'price': 129.99,
            'category': categories[3],  # Home & Garden
            'stock_quantity': 80,
            'seller': admin_user
        },
        {
            'name': 'LED Desk Lamp',
            'description': 'Adjustable LED desk lamp with multiple brightness levels',
            'short_description': 'Modern LED desk lamp',
            'sku': 'LAMP-LED-001',
            'price': 39.99,
            'category': categories[3],  # Home & Garden
            'stock_quantity': 120,
            'seller': admin_user
        },
        {
            'name': 'Yoga Mat Premium',
            'description': 'High-quality yoga mat with non-slip surface',
            'short_description': 'Non-slip premium yoga mat',
            'sku': 'YOGA-MAT-001',
            'price': 34.99,
            'category': categories[4],  # Sports & Outdoors
            'stock_quantity': 90,
            'seller': admin_user
        }
    ]
    
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            sku=product_data['sku'],
            defaults=product_data
        )
        if created:
            print(f"Created product: {product.name} - ${product.price}")
    
    print("\nSample data creation completed!")
    print(f"Created {Category.objects.count()} categories")
    print(f"Created {Product.objects.count()} products")
    print(f"Created {User.objects.count()} users")

if __name__ == '__main__':
    create_sample_data()