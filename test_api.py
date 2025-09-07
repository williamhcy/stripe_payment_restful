#!/usr/bin/env python3
"""
Test script to verify Stripe REST API calls work correctly
Run this script to test the API connection before starting the main application
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_stripe_api():
    """Test Stripe API connection and basic functionality"""
    
    stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
    
    if not stripe_secret_key:
        print("❌ Error: STRIPE_SECRET_KEY not found in environment variables")
        print("Please create a .env file with your Stripe secret key")
        return False
    
    print(f"🔑 Using Stripe Secret Key: {stripe_secret_key[:12]}...")
    
    # Test 1: List customers (basic API connection test)
    print("\n📋 Test 1: Testing API connection...")
    try:
        response = requests.get(
            'https://api.stripe.com/v1/customers?limit=1',
            headers={
                'Authorization': f'Bearer {stripe_secret_key}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        
        if response.status_code == 200:
            print("✅ API connection successful!")
            data = response.json()
            print(f"   Found {data.get('data', [])} customers")
        else:
            print(f"❌ API connection failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API connection test failed: {str(e)}")
        return False
    
    # Test 2: Create a test customer
    print("\n👤 Test 2: Creating test customer...")
    try:
        response = requests.post(
            'https://api.stripe.com/v1/customers',
            headers={
                'Authorization': f'Bearer {stripe_secret_key}',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'email': 'test@example.com',
                'name': 'Test Customer'
            }
        )
        
        if response.status_code == 200:
            print("✅ Test customer created successfully!")
            data = response.json()
            print(f"   Customer ID: {data['id']}")
            customer_id = data['id']
        else:
            print(f"❌ Customer creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Customer creation test failed: {str(e)}")
        return False
    
    # Test 3: Create a test payment intent
    print("\n💳 Test 3: Creating test payment intent...")
    try:
        response = requests.post(
            'https://api.stripe.com/v1/payment_intents',
            headers={
                'Authorization': f'Bearer {stripe_secret_key}',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'amount': '1000',  # $10.00 in cents
                'currency': 'usd',
                'metadata[test]': 'true'
            }
        )
        
        if response.status_code == 200:
            print("✅ Test payment intent created successfully!")
            data = response.json()
            print(f"   Payment Intent ID: {data['id']}")
            print(f"   Client Secret: {data['client_secret'][:20]}...")
            payment_intent_id = data['id']
        else:
            print(f"❌ Payment intent creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Payment intent creation test failed: {str(e)}")
        return False
    
    # Test 4: Retrieve the payment intent
    print("\n🔍 Test 4: Retrieving payment intent...")
    try:
        response = requests.get(
            f'https://api.stripe.com/v1/payment_intents/{payment_intent_id}',
            headers={
                'Authorization': f'Bearer {stripe_secret_key}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        
        if response.status_code == 200:
            print("✅ Payment intent retrieved successfully!")
            data = response.json()
            print(f"   Status: {data['status']}")
            print(f"   Amount: ${data['amount']/100:.2f} {data['currency'].upper()}")
        else:
            print(f"❌ Payment intent retrieval failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Payment intent retrieval test failed: {str(e)}")
        return False
    
    print("\n🎉 All tests passed! Your Stripe API integration is working correctly.")
    print("\n📝 Next steps:")
    print("   1. Update your .env file with the correct publishable key")
    print("   2. Update the publishable key in templates/index.html")
    print("   3. Run: python app.py")
    print("   4. Visit: http://localhost:5000")
    
    return True

if __name__ == '__main__':
    print("🧪 Stripe REST API Test Suite")
    print("=" * 40)
    
    success = test_stripe_api()
    
    if not success:
        print("\n❌ Tests failed. Please check your configuration.")
        exit(1)
