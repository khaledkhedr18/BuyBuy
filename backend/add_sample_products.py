import os
import django
import sys
from decimal import Decimal

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from authentication.models import User
from categories.models import Category
from products.models import Product

def main():
    print("Creating sample products...")

    # Get our superuser
    try:
        seller = User.objects.get(username='khaledkhedr1511')
    except User.DoesNotExist:
        print("Superuser not found. Create one first with 'python manage.py createsuperuser'")
        return

    # Get a category (create one if none exists)
    category = Category.objects.first()
    if not category:
        category = Category.objects.create(
            name="Electronics",
            description="Electronic devices and accessories",
            is_active=True
        )
        print("Created Electronics category")

    # Sample products
    products_data = [
        {
            'name': 'iPhone 15 Pro',
            'description': 'Latest iPhone with Pro camera system, titanium design, and A17 Pro chip.',
            'price': Decimal('999.99'),
            'stock_quantity': 15,
            'category': category,
        },
        {
            'name': 'MacBook Air M3',
            'description': 'Powerful and lightweight laptop with M3 chip, perfect for work and creativity.',
            'price': Decimal('1299.99'),
            'stock_quantity': 8,
            'category': category,
        },
        {
            'name': 'AirPods Pro',
            'description': 'Wireless earbuds with Active Noise Cancellation and Spatial Audio.',
            'price': Decimal('249.99'),
            'stock_quantity': 25,
            'category': category,
        },
        {
            'name': 'iPad Pro 12.9"',
            'description': 'Professional tablet with M2 chip, Liquid Retina XDR display.',
            'price': Decimal('1099.99'),
            'stock_quantity': 12,
            'category': category,
        },
        {
            'name': 'Apple Watch Series 9',
            'description': 'Advanced health and fitness features with beautiful Always-On Retina display.',
            'price': Decimal('399.99'),
            'stock_quantity': 20,
            'category': category,
        },
    ]

    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            seller=seller,
            defaults=product_data
        )
        if created:
            print(f"Created product: {product.name}")
        else:
            print(f"Product already exists: {product.name}")

    print(f"\nTotal products in database: {Product.objects.count()}")
    print("Sample products created successfully!")

if __name__ == '__main__':
    main()
