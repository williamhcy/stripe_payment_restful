from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Stripe API configuration
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_API_BASE_URL = 'https://api.stripe.com/v1'

def make_stripe_request(method, endpoint, data=None):
    """
    Make a request to Stripe REST API with detailed logging
    
    Args:
        method (str): HTTP method (GET, POST, etc.)
        endpoint (str): API endpoint (e.g., 'payment_intents')
        data (dict): Request data for POST requests
    
    Returns:
        tuple: (response_data, status_code, error_message)
    """
    url = f"{STRIPE_API_BASE_URL}/{endpoint}"
    headers = {
        'Authorization': f'Bearer {STRIPE_SECRET_KEY}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Log request details
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*80}")
    print(f"🔵 STRIPE API REQUEST - {timestamp}")
    print(f"{'='*80}")
    print(f"📡 Method: {method.upper()}")
    print(f"🌐 URL: {url}")
    print(f"📋 Headers:")
    for key, value in headers.items():
        if key == 'Authorization':
            # Mask the secret key for security
            masked_key = value[:20] + "..." + value[-4:] if len(value) > 24 else "***"
            print(f"   {key}: {masked_key}")
        else:
            print(f"   {key}: {value}")
    
    if data:
        print(f"📦 Request Data:")
        for key, value in data.items():
            print(f"   {key}: {value}")
    else:
        print(f"📦 Request Data: None")
    
    try:
        # Make the request
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, data=data)
        else:
            error_msg = f"Unsupported HTTP method: {method}"
            print(f"❌ Error: {error_msg}")
            return None, 400, error_msg
        
        # Log response details
        print(f"\n📥 RESPONSE RECEIVED:")
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        # Parse response data
        try:
            response_data = response.json()
            print(f"📄 Response Body (JSON):")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            response_data = {"raw_response": response.text}
            print(f"📄 Response Body (Raw Text):")
            print(response.text)
        
        # Check for errors
        if response.status_code >= 400:
            error_msg = response_data.get('error', {}).get('message', 'Unknown error')
            print(f"\n❌ API Error: {error_msg}")
            print(f"{'='*80}\n")
            return None, response.status_code, error_msg
        
        print(f"\n✅ Request Successful!")
        print(f"{'='*80}\n")
        return response_data, response.status_code, None
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Request failed: {str(e)}"
        print(f"\n❌ Network Error: {error_msg}")
        print(f"{'='*80}\n")
        return None, 500, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"\n❌ Unexpected Error: {error_msg}")
        print(f"{'='*80}\n")
        return None, 500, error_msg

@app.route('/')
def index():
    """Main page with payment form"""
    return render_template('index.html')

@app.route('/checkout')
def checkout():
    """Checkout page with Stripe Checkout"""
    return render_template('checkout.html')

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create a Stripe Checkout session"""
    try:
        # Log incoming request
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"🎯 FLASK ROUTE: /create-checkout-session - {timestamp}")
        print(f"{'='*60}")
        
        data = request.get_json()
        print(f"📥 Incoming Request Data:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        amount = data.get('amount')
        currency = data.get('currency', 'usd')
        customer_name = data.get('customer_name')
        customer_email = data.get('customer_email')
        
        print(f"💰 Extracted Values:")
        print(f"   Amount: {amount}")
        print(f"   Currency: {currency}")
        print(f"   Customer Name: {customer_name}")
        print(f"   Customer Email: {customer_email}")
        
        # Validate amount
        if not amount or amount <= 0:
            print(f"❌ Validation Error: Invalid amount")
            return jsonify({'error': 'Invalid amount'}), 400
        
        # Prepare data for Stripe Checkout Session
        random_id = str(datetime.now().timestamp())
        stripe_data = {
            'payment_method_types[0]': 'card',
            'payment_method_types[1]': 'alipay',
            'payment_method_types[2]': 'wechat_pay',
            'payment_method_options[wechat_pay][client]':'web',
        #    'client_reference_id': random_id,
            'line_items[0][price_data][currency]': currency,
            'line_items[0][price_data][product_data][name]': 'Payment',
            'line_items[0][price_data][unit_amount]': int(amount * 100),  # Convert to cents
            'line_items[0][quantity]': '1',
            'mode': 'payment',
            'success_url': request.url_root + 'payment-success?session_id={CHECKOUT_SESSION_ID}',
            'cancel_url': request.url_root + 'payment-cancel',
        #    'customer_email': customer_email,
        #    'metadata[customer_name]': customer_name,
            'metadata[integration_check]': 'accept_a_payment'
        }
        
        print(f"🔄 Prepared Stripe Checkout Data:")
        print(json.dumps(stripe_data, indent=2, ensure_ascii=False))
        
        # Make request to Stripe API
        response_data, status_code, error = make_stripe_request('POST', 'checkout/sessions', stripe_data)
        
        if error:
            print(f"❌ Stripe API Error: {error}")
            return jsonify({'error': error}), status_code
        
        result = {
            'checkout_url': response_data['url'],
            'session_id': response_data['id']
        }
        
        print(f"✅ Returning Response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"{'='*60}\n")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """Create a payment intent using Stripe REST API"""
    try:
        # Log incoming request
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"🎯 FLASK ROUTE: /create-payment-intent - {timestamp}")
        print(f"{'='*60}")
        
        data = request.get_json()
        print(f"📥 Incoming Request Data:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        amount = data.get('amount')
        currency = data.get('currency', 'usd')
        
        print(f"💰 Extracted Values:")
        print(f"   Amount: {amount}")
        print(f"   Currency: {currency}")
        
        # Validate amount
        if not amount or amount <= 0:
            print(f"❌ Validation Error: Invalid amount")
            return jsonify({'error': 'Invalid amount'}), 400
        
        # Prepare data for Stripe API
        stripe_data = {
            'amount': int(amount * 100),  # Convert to cents
            'currency': currency,
            'automatic_payment_methods[enabled]': 'true',
            'automatic_payment_methods[allow_redirects]': 'always',
            'metadata[integration_check]': 'accept_a_payment'
        }
        
        print(f"🔄 Prepared Stripe Data:")
        print(json.dumps(stripe_data, indent=2, ensure_ascii=False))
        
        # Make request to Stripe API
        response_data, status_code, error = make_stripe_request('POST', 'payment_intents', stripe_data)
        
        if error:
            print(f"❌ Stripe API Error: {error}")
            return jsonify({'error': error}), status_code
        
        result = {
            'client_secret': response_data['client_secret'],
            'payment_intent_id': response_data['id']
        }
        
        print(f"✅ make_stripe_request Returning Response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"{'='*60}\n")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/update-payment-intent', methods=['POST'])
def update_payment_intent():
    """Update a payment intent with a payment method"""
    try:
        # Log incoming request
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"🎯 FLASK ROUTE: /update-payment-intent - {timestamp}")
        print(f"{'='*60}")
        
        data = request.get_json()
        print(f"📥 Incoming Request Data:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        payment_intent_id = data.get('payment_intent_id')
        payment_method = data.get('payment_method')
        
        print(f"🔍 Extracted Values:")
        print(f"   Payment Intent ID: {payment_intent_id}")
        print(f"   Payment Method: {payment_method}")
        
        if not payment_intent_id or not payment_method:
            print(f"❌ Validation Error: Payment intent ID and payment method required")
            return jsonify({'error': 'Payment intent ID and payment method required'}), 400
        
        # Prepare data for Stripe API to update payment intent
        stripe_data = {
            'payment_method': payment_method
        }
        
        print(f"🔄 Prepared Stripe Data for Update:")
        print(json.dumps(stripe_data, indent=2, ensure_ascii=False))
        
        # Update the payment intent with Stripe API
        response_data, status_code, error = make_stripe_request('POST', f'payment_intents/{payment_intent_id}', stripe_data)
        
        if error:
            print(f"❌ Stripe API Error: {error}")
            return jsonify({'error': error}), status_code
        
        result = {
            'status': response_data['status'],
            'amount': response_data['amount'],
            'currency': response_data['currency'],
            'payment_method': response_data.get('payment_method'),
            'payment_intent_id': response_data['id']
        }
        
        print(f"✅ update-payment-intent Returning Response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"{'='*60}\n")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    """Confirm a payment intent with payment method"""
    try:
        # Log incoming request
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"🎯 FLASK ROUTE: /confirm-payment - {timestamp}")
        print(f"{'='*60}")
        
        data = request.get_json()
        print(f"📥 Incoming Request Data:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        payment_intent_id = data.get('payment_intent_id')
        payment_method_data = data.get('payment_method')
        
        print(f"🔍 Extracted Values:")
        print(f"   Payment Intent ID: {payment_intent_id}")
        print(f"   Payment Method Data: {payment_method_data}")
        
        if not payment_intent_id:
            print(f"❌ Validation Error: Payment intent ID required")
            return jsonify({'error': 'Payment intent ID required'}), 400
        
        # Prepare data for Stripe API to confirm payment
        stripe_data = {}
        if payment_method_data:
            stripe_data['payment_method'] = payment_method_data
        
        print(f"🔄 Prepared Stripe Data for Confirmation:")
        print(json.dumps(stripe_data, indent=2, ensure_ascii=False))
        
        # Confirm the payment intent with Stripe API
        response_data, status_code, error = make_stripe_request('POST', f'payment_intents/{payment_intent_id}/confirm', stripe_data)
        
        if error:
            print(f"❌ Stripe API Error: {error}")
            return jsonify({'error': error}), status_code
        
        result = {
            'status': response_data['status'],
            'amount': response_data['amount'],
            'currency': response_data['currency'],
            'payment_method': response_data.get('payment_method'),
            'payment_intent_id': response_data['id']
        }
        
        print(f"✅ confirm-payment Returning Response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"{'='*60}\n")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/create-customer', methods=['POST'])
def create_customer():
    """Create a Stripe customer"""
    try:
        # Log incoming request
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"🎯 FLASK ROUTE: /create-customer - {timestamp}")
        print(f"{'='*60}")
        
        data = request.get_json()
        print(f"📥 Incoming Request Data:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        email = data.get('email')
        name = data.get('name')
        
        print(f"👤 Extracted Values:")
        print(f"   Email: {email}")
        print(f"   Name: {name}")
        
        if not email:
            print(f"❌ Validation Error: Email is required")
            return jsonify({'error': 'Email is required'}), 400
        
        # Prepare data for Stripe API
        stripe_data = {'email': email}
        if name:
            stripe_data['name'] = name
        
        print(f"🔄 Prepared Stripe Data:")
        print(json.dumps(stripe_data, indent=2, ensure_ascii=False))
        
        # Make request to Stripe API
        response_data, status_code, error = make_stripe_request('POST', 'customers', stripe_data)
        
        if error:
            print(f"❌ Stripe API Error: {error}")
            return jsonify({'error': error}), status_code
        
        result = {
            'customer_id': response_data['id'],
            'email': response_data['email'],
            'name': response_data.get('name')
        }
        
        print(f"✅ Returning Response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"{'='*60}\n")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/retrieve-payment-intent/<payment_intent_id>')
def retrieve_payment_intent(payment_intent_id):
    """Retrieve a payment intent by ID"""
    try:
        response_data, status_code, error = make_stripe_request('GET', f'payment_intents/{payment_intent_id}')
        
        if error:
            return jsonify({'error': error}), status_code
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/list-payment-intents')
def list_payment_intents():
    """List recent payment intents"""
    try:
        response_data, status_code, error = make_stripe_request('GET', 'payment_intents?limit=10')
        
        if error:
            return jsonify({'error': error}), status_code
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/list-customers')
def list_customers():
    """List recent customers"""
    try:
        response_data, status_code, error = make_stripe_request('GET', 'customers?limit=10')
        
        if error:
            return jsonify({'error': error}), status_code
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/payment-success')
def payment_success():
    """Payment success page"""
    #call the api to get the payment details
    session_id = request.args.get('session_id')
    response_data, status_code, error = make_stripe_request('GET', f'checkout/sessions/{session_id}')
    print(f"📥 Payment Details:")
    print(json.dumps(response_data, indent=2, ensure_ascii=False))  
    print(f"📥 Payment ID:")
    print(response_data["payment_intent"])
    if error:
        return jsonify({'error': error}), status_code
    return render_template('success.html', payment_id=response_data["payment_intent"])

@app.route('/payment-cancel')
def payment_cancel():
    """Payment cancellation page"""
    return render_template('cancel.html')

@app.route('/api-status')
def api_status():
    """Check API connection status"""
    try:
        # Log incoming request
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"🎯 FLASK ROUTE: /api-status - {timestamp}")
        print(f"{'='*60}")
        print(f"📥 Incoming Request: GET /api-status")
        print(f"🔍 Testing Stripe API connection...")
        
        # Test API connection by listing customers with limit 1
        response_data, status_code, error = make_stripe_request('GET', 'customers?limit=1')
        
        if error:
            result = {
                'status': 'error',
                'message': error,
                'status_code': status_code
            }
            print(f"❌ API Status Check Failed:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print(f"{'='*60}\n")
            return jsonify(result), status_code
        
        result = {
            'status': 'success',
            'message': 'Stripe API connection successful',
            'status_code': status_code
        }
        
        print(f"✅ API Status Check Successful:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"{'='*60}\n")
        
        return jsonify(result)
        
    except Exception as e:
        result = {
            'status': 'error',
            'message': f'Connection failed: {str(e)}',
            'status_code': 500
        }
        print(f"❌ Unexpected Error in API Status Check:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"{'='*60}\n")
        return jsonify(result), 500

if __name__ == '__main__':

    port = int(os.getenv('PORT', 5500))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_ENV') != 'production'
    # HTTPS configuration
    ssl_context = None
    if os.getenv('HTTPS_ENABLED', 'false').lower() == 'true':
        ssl_cert = os.getenv('SSL_CERT_PATH', 'cert.pem')
        ssl_key = os.getenv('SSL_KEY_PATH', 'key.pem')

    if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        ssl_context = (ssl_cert, ssl_key)

    if ssl_context:
        print("run in SSL mode")
        app.run(host=host, port=port, debug=debug, ssl_context=ssl_context)
    else:
        app.run(debug=True, host='0.0.0.0', port=5500)