# Stripe Payment Processing Demo

A complete Python Flask application that demonstrates secure payment processing using Stripe.js for frontend tokenization and Stripe's REST API for backend processing. This project ensures PCI compliance by never handling raw card data on your server.

## Features

- 💳 **Dual Payment Methods** - Choose between embedded form or Stripe Checkout
- 🛒 **Stripe Checkout** - Redirect to Stripe's hosted payment page
- 🎨 **Modern UI** - Beautiful, responsive design with gradient backgrounds
- 👤 **Customer Management** - Creates Stripe customers for better tracking
- 🔒 **PCI Compliant** - Card data never touches your server
- 📱 **Mobile Friendly** - Responsive design that works on all devices
- ⚡ **Real-time Validation** - Live card validation using Stripe Elements
- 🧪 **Built-in Testing** - Test script to verify API connectivity

## Project Structure

```
stripe_prj/
├── app.py                 # Main Flask application with REST API calls
├── test_api.py           # Test script for API connectivity
├── requirements.txt       # Python dependencies (no Stripe SDK)
├── env_example.txt        # Environment variables template
├── README.md             # This file
└── templates/
    ├── index.html        # Main payment form (embedded)
    ├── checkout.html     # Stripe Checkout form
    ├── success.html      # Payment success page
    └── cancel.html       # Payment cancellation page
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Stripe Account

1. Create a Stripe account at [https://stripe.com](https://stripe.com)
2. Get your API keys from the [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
3. Copy `env_example.txt` to `.env` and fill in your keys:

```bash
cp env_example.txt .env
```

Edit `.env` with your actual Stripe keys:
```
STRIPE_SECRET_KEY=sk_test_your_actual_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_publishable_key_here
```

### 3. Update Frontend Configuration

Edit `templates/index.html` and replace the placeholder publishable key:

```javascript
const stripe = Stripe('pk_test_your_actual_publishable_key_here');
```

### 4. Test API Connection (Optional but Recommended)

```bash
python test_api.py
```

This will test your Stripe API connection and verify everything is working correctly.

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Payment Methods

This application offers two different payment approaches:

### 1. 🎨 Embedded Payment Form (`/`)
- **Custom UI**: Payment form embedded in your website
- **Stripe Elements**: Secure card input fields
- **Real-time Validation**: Live card validation
- **Custom Styling**: Matches your website design
- **More Control**: Full control over user experience

### 2. 🛒 Stripe Checkout (`/checkout`)
- **Hosted Page**: Redirects to Stripe's secure payment page
- **Zero PCI**: No card data touches your server
- **Mobile Optimized**: Automatically optimized for mobile
- **Multiple Payment Methods**: Supports cards, wallets, bank transfers
- **Less Code**: Minimal implementation required

## REST API Implementation

This project uses direct HTTP requests to Stripe's REST API instead of the official Stripe Python SDK. Here's how it works:

### Payment Method Configuration

The PaymentIntent is configured to:
- ✅ **Enable automatic payment methods**: Accepts cards and other payment methods
- ✅ **Allow redirects**: Supports 3D Secure authentication and other redirect-based methods
- ✅ **Return URL**: Provided during payment confirmation (not during creation)
- ✅ **Enhanced Security**: Supports Strong Customer Authentication (SCA) requirements

**Important:** The `return_url` is provided during payment confirmation in the frontend using `stripe.confirmPayment()`, not during PaymentIntent creation. This ensures compliance with international payment regulations while maintaining security.

### HTTP Request Structure

All Stripe API calls are made using the `requests` library with the following structure:

```python
def make_stripe_request(method, endpoint, data=None):
    url = f"https://api.stripe.com/v1/{endpoint}"
    headers = {
        'Authorization': f'Bearer {STRIPE_SECRET_KEY}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    if method.upper() == 'POST':
        response = requests.post(url, headers=headers, data=data)
    elif method.upper() == 'GET':
        response = requests.get(url, headers=headers)
    
    return response.json(), response.status_code, error_message
```

### Example API Calls

**Create Payment Intent:**
```python
# Equivalent to: curl -X POST https://api.stripe.com/v1/payment_intents
data = {
    'amount': '1000',
    'currency': 'usd',
    'automatic_payment_methods[enabled]': 'true',
    'automatic_payment_methods[allow_redirects]': 'always',
    'metadata[integration_check]': 'accept_a_payment'
}
response_data, status_code, error = make_stripe_request('POST', 'payment_intents', data)
```

**Note:** The `return_url` is provided during payment confirmation in the frontend, not during PaymentIntent creation.

**Create Customer:**
```python
# Equivalent to: curl -X POST https://api.stripe.com/v1/customers
data = {
    'email': 'customer@example.com',
    'name': 'John Doe'
}
response_data, status_code, error = make_stripe_request('POST', 'customers', data)
```

**Retrieve Payment Intent:**
```python
# Equivalent to: curl https://api.stripe.com/v1/payment_intents/pi_xxx
response_data, status_code, error = make_stripe_request('GET', f'payment_intents/{payment_intent_id}')
```

## API Endpoints

### POST `/create-payment-intent`
Creates a Stripe PaymentIntent for processing payments.

**Request Body:**
```json
{
    "amount": 10.00,
    "currency": "usd"
}
```

**Response:**
```json
{
    "client_secret": "pi_xxx_secret_xxx",
    "payment_intent_id": "pi_xxx"
}
```

### POST `/create-customer`
Creates a Stripe customer for better payment tracking.

**Request Body:**
```json
{
    "name": "John Doe",
    "email": "john@example.com"
}
```

**Response:**
```json
{
    "customer_id": "cus_xxx",
    "email": "john@example.com",
    "name": "John Doe"
}
```

### POST `/update-payment-intent`
Updates a payment intent with a payment method.

**Request Body:**
```json
{
    "payment_intent_id": "pi_xxx",
    "payment_method": "pm_xxx"
}
```

**Response:**
```json
{
    "status": "requires_confirmation",
    "amount": 1000,
    "currency": "usd",
    "payment_method": "pm_xxx",
    "payment_intent_id": "pi_xxx"
}
```

### POST `/confirm-payment`
Retrieves payment intent status and details.

**Request Body:**
```json
{
    "payment_intent_id": "pi_xxx"
}
```

### GET `/retrieve-payment-intent/<payment_intent_id>`
Retrieves a specific payment intent by ID.

### GET `/list-payment-intents`
Lists recent payment intents (limit 10).

### GET `/list-customers`
Lists recent customers (limit 10).

### GET `/api-status`
Checks Stripe API connection status.

## Testing

### API Connection Test

Before running the main application, test your Stripe API connection:

```bash
python test_api.py
```

This script will:
- Test API connectivity
- Create a test customer
- Create a test payment intent
- Retrieve the payment intent
- Verify all operations work correctly

### Test Cards

Use these test card numbers for testing:

- **Successful Payment:** `4242 4242 4242 4242`
- **Declined Payment:** `4000 0000 0000 0002`
- **Requires Authentication:** `4000 0025 0000 3155`

Use any future expiry date and any 3-digit CVC.

### Test Scenarios

1. **Successful Payment Flow:**
   - Enter customer information
   - Use test card `4242 4242 4242 4242`
   - Complete payment → Redirects to success page

2. **Declined Payment:**
   - Use test card `4000 0000 0000 0002`
   - Payment will be declined with error message

3. **3D Secure Authentication:**
   - Use test card `4000 0025 0000 3155`
   - Customer will be redirected to 3D Secure authentication
   - After authentication, redirected back to success page

4. **International Cards:**
   - Use test cards from different countries
   - May trigger additional authentication flows
   - All handled automatically with redirects

## Security Considerations

- ✅ **PCI Compliant**: Card data never touches your server (handled by Stripe.js)
- ✅ **Secure Tokenization**: Uses Stripe.js to create payment method tokens
- ✅ **No Raw Card Data**: Never send credit card numbers directly to your API
- ✅ **Environment Variables**: Secret keys stored securely
- ✅ **HTTPS Required**: Use HTTPS in production
- ✅ **Input Validation**: All inputs validated on server side
- ✅ **Error Handling**: Proper error handling and logging
- ✅ **Webhook System**: Use Stripe webhooks for production

## Production Deployment

For production deployment:

1. **Use Live Keys:** Replace test keys with live keys
2. **Enable HTTPS:** Ensure your application uses HTTPS
3. **Set Up Webhooks:** Configure Stripe webhooks for payment events
4. **Environment Variables:** Use proper environment variable management
5. **Error Monitoring:** Implement proper logging and monitoring

## Stripe Dashboard

Monitor your payments and transactions in the [Stripe Dashboard](https://dashboard.stripe.com):

- **Payments:** View all payment attempts and their status
- **Customers:** Manage customer information
- **Events:** Monitor webhook events and API calls
- **Analytics:** Track payment success rates and revenue

## Troubleshooting

### Common Issues

1. **"Invalid API Key" Error:**
   - Check that your API keys are correct
   - Ensure you're using the right key (test vs live)

2. **CORS Issues:**
   - Make sure your domain is added to Stripe's allowed origins

3. **Payment Declined:**
   - Check the Stripe Dashboard for decline reasons
   - Use test cards for development

4. **Frontend Not Loading:**
   - Check browser console for JavaScript errors
   - Verify publishable key is correct

## Support

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe API Reference](https://stripe.com/docs/api)
- [Stripe Test Cards](https://stripe.com/docs/testing)

## License

This project is for educational purposes. Please ensure compliance with Stripe's terms of service for production use.
