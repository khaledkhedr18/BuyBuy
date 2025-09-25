#!/usr/bin/env python3
"""
Test script to verify checkout address handling
"""

def test_shipping_address_formatting():
    """Test that address fields are properly combined"""

    # Simulate form data from checkout
    form_data = {
        'address': 'sdfasdfasdf',
        'city': 'dafsdfaf',
        'state': 'dasfasdfas',
        'zip_code': '4312414',
        'country': 'CA'
    }

    # Simulate the logic from the fixed checkout view
    address_parts = []
    if form_data.get('address', '').strip():
        address_parts.append(form_data['address'].strip())
    if form_data.get('city', '').strip():
        address_parts.append(form_data['city'].strip())
    if form_data.get('state', '').strip():
        address_parts.append(form_data['state'].strip())
    if form_data.get('zip_code', '').strip():
        address_parts.append(form_data['zip_code'].strip())
    if form_data.get('country', '').strip():
        address_parts.append(form_data['country'].strip())

    shipping_address = ', '.join(address_parts)

    print("Test form data:")
    for key, value in form_data.items():
        print(f"  {key}: '{value}'")

    print(f"\nGenerated shipping_address:")
    print(f"  '{shipping_address}'")

    print(f"\nShipping address is valid: {bool(shipping_address)}")

    return shipping_address

if __name__ == '__main__':
    test_shipping_address_formatting()
