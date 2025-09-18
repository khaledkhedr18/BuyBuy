import os
import django
import sys
from django.utils import timezone
from faker import Faker

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from authentication.models import User, UserProfile, JWTToken
from categories.models import Category

fake = Faker()

def create_users(num_users=10):
    """Create sample users and profiles"""
    users = []
    for _ in range(num_users):
        user = User.objects.create_user(
            email=fake.email(),
            username=fake.user_name(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password='testpass123'
        )
        UserProfile.objects.create(
            user=user,
            phone=fake.numerify(text='###-###-#####'),
            address=fake.address(),
            city=fake.city(),
            state=fake.state(),
            country=fake.country(),
            postal_code=fake.postcode(),
            date_of_birth=fake.date_of_birth(),
            avatar_url=fake.image_url(),
            bio=fake.text()
        )
        users.append(user)
    return users

def create_categories():
    """Create sample categories with hierarchy"""
    categories = []

    # Create main categories
    main_categories = [
        "Electronics", "Clothing", "Home & Kitchen",
        "Books", "Sports & Outdoors", "Beauty & Health"
    ]

    for name in main_categories:
        cat = Category.objects.create(
            name=name,
            description=fake.text(),
            is_active=True,
            sort_order=fake.random_digit()
        )
        categories.append(cat)

    # Create sub-categories for each main category
    subcategories = {
        "Electronics": ["Smartphones", "Laptops", "Headphones", "Cameras"],
        "Clothing": ["Men's Fashion", "Women's Fashion", "Kids' Fashion", "Accessories"],
        "Home & Kitchen": ["Furniture", "Kitchen Appliances", "Home Decor", "Bedding"],
        "Books": ["Fiction", "Non-Fiction", "Educational", "Children's Books"],
        "Sports & Outdoors": ["Exercise Equipment", "Outdoor Gear", "Team Sports", "Camping"],
        "Beauty & Health": ["Skincare", "Makeup", "Hair Care", "Vitamins & Supplements"]
    }

    for parent in categories:
        if parent.name in subcategories:
            for sub_name in subcategories[parent.name]:
                child = Category.objects.create(
                    name=sub_name,
                    description=fake.text(),
                    parent=parent,
                    is_active=True,
                    sort_order=fake.random_digit()
                )
                categories.append(child)

    return categories

def create_jwt_tokens(users):
    """Create sample JWT tokens"""
    tokens = []
    for user in users:
        for _ in range(2):
            token = JWTToken.objects.create(
                user=user,
                token_hash=fake.sha256(),
                expires_at=timezone.now() + timezone.timedelta(days=1),
                is_revoked=fake.boolean(chance_of_getting_true=25)
            )
            tokens.append(token)
    return tokens

def main():
    print("Creating sample data for BuyBuy...")

    # Create superuser
    try:
        admin = User.objects.create_superuser(
            email='admin@buybuy.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            password='adminpass'
        )
        UserProfile.objects.create(user=admin)
        print("Created admin user: admin@buybuy.com / adminpass")
    except Exception as e:
        print(f"Admin user might already exist: {e}")

    # Create regular users
    users = create_users(15)
    print(f"Created {len(users)} regular users")

    # Create categories
    categories = create_categories()
    print(f"Created {len(categories)} categories")

    # Create JWT tokens
    tokens = create_jwt_tokens(users[:5])  # Tokens for first 5 users
    print(f"Created {len(tokens)} JWT tokens")

    print("\nSample data created successfully!")
    print(f"Total users: {User.objects.count()}")
    print(f"Total categories: {Category.objects.count()}")
    print(f"Total JWT tokens: {JWTToken.objects.count()}")

if __name__ == '__main__':
    main()
