#!/usr/bin/env python3
"""
Simple test script to verify that the edit_product and delete_product URLs are working.
This will test URL resolution without requiring a web browser.
"""

import os
import sys
import django
from django.conf import settings
from django.urls import reverse

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append('/home/khaled/Desktop/Software Courses/BuyBuy/backend')
django.setup()

def test_urls():
    """Test that the new URL patterns work correctly"""
    try:
        # Test edit_product URL
        edit_url = reverse('products:edit_product', args=[1])
        print(f"✅ edit_product URL resolved: {edit_url}")

        # Test delete_product URL
        delete_url = reverse('products:delete_product', args=[1])
        print(f"✅ delete_product URL resolved: {delete_url}")

        print(f"\n🎉 SUCCESS: Both URLs are working correctly!")
        print(f"The NoReverseMatch error has been fixed.")

        return True
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == '__main__':
    test_urls()
