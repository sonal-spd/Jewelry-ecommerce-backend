# Stripe Webhook Configuration Guide

This guide explains how to configure Stripe webhooks for your application.

## Webhook URL

### Production URL
```
https://api.lulibyveronica.com/payments/webhook/
```
or
```
https://your-production-domain.com/payments/webhook/
```

### Local Testing URL
For local development, use Stripe CLI (see below) or use a tunneling service like ngrok:
```
https://your-ngrok-url.ngrok.io/payments/webhook/
```

---

## Required Webhook Events

Configure these events in your Stripe Dashboard:

### For Checkout Sessions (Recommended)
- ✅ **`checkout.session.completed`** - When a checkout session is successfully completed

### For Payment Intents (If using embedded payment form)
- ✅ **`payment_intent.succeeded`** - When a payment intent succeeds
- ✅ **`payment_intent.payment_failed`** - When a payment intent fails

### Recommended Events (Select All)
Select these events in Stripe Dashboard:

1. **`checkout.session.completed`** ⭐ (Required for Checkout Sessions)
2. **`payment_intent.succeeded`** (Required for Payment Intents)
3. **`payment_intent.payment_failed`** (Required for Payment Intents)

---

## Step-by-Step Configuration

### 1. Go to Stripe Dashboard

1. Log in to [https://dashboard.stripe.com](https://dashboard.stripe.com)
2. Make sure you're in **Test Mode** (toggle in top right) for testing
3. Or **Live Mode** for production

### 2. Navigate to Webhooks

1. Click **"Developers"** in the left sidebar
2. Click **"Webhooks"**

### 3. Add Endpoint

1. Click **"+ Add endpoint"** button
2. Enter your webhook URL:
   ```
   https://api.lulibyveronica.com/payments/webhook/
   ```
   (Replace with your actual backend URL)

### 4. Select Events

Select these events:
- ✅ `checkout.session.completed`
- ✅ `payment_intent.succeeded`
- ✅ `payment_intent.payment_failed`

### 5. Add Endpoint

Click **"Add endpoint"**

### 6. Get Webhook Secret

1. After creating the endpoint, click on it to view details
2. Find **"Signing secret"** section
3. Click **"Reveal"** button
4. Copy the secret (starts with `whsec_`)

### 7. Add to Settings

Add the webhook secret to your `.env` file or `settings.py`:

**Option 1: Environment Variable (Recommended)**
```env
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Option 2: Direct in settings.py**
```python
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
```

---

## Test Mode vs Live Mode

### Important Notes

- **Test Mode**: Use test webhook secrets (starts with `whsec_test_`)
- **Live Mode**: Use live webhook secrets (starts with `whsec_live_`)

**You need separate webhook endpoints for:**
- Test mode (for development/testing)
- Live mode (for production)

**Current Configuration:**
Your `settings.py` shows:
```python
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='whsec_6BxRQHgIUXx3vr2qXA51w3gXBJV63uOI')
```

Make sure this matches the webhook secret from your Stripe Dashboard!

---

## Local Development Setup

### Option 1: Stripe CLI (Recommended)

1. **Install Stripe CLI**: [https://stripe.com/docs/stripe-cli](https://stripe.com/docs/stripe-cli)

2. **Login to Stripe CLI**:
   ```bash
   stripe login
   ```

3. **Forward webhooks to local server**:
   ```bash
   stripe listen --forward-to localhost:8000/payments/webhook/
   ```

4. **Copy the webhook signing secret** that appears (starts with `whsec_`)

5. **Use this secret** in your local `.env` file:
   ```env
   STRIPE_WEBHOOK_SECRET=whsec_xxx_from_stripe_cli
   ```

### Option 2: ngrok (Alternative)

1. **Install ngrok**: [https://ngrok.com](https://ngrok.com)

2. **Start your Django server**:
   ```bash
   python manage.py runserver
   ```

3. **Start ngrok**:
   ```bash
   ngrok http 8000
   ```

4. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

5. **Configure in Stripe Dashboard**:
   - Webhook URL: `https://abc123.ngrok.io/payments/webhook/`
   - Select events: `checkout.session.completed`, `payment_intent.succeeded`, `payment_intent.payment_failed`
   - Copy the webhook secret

---

## Verifying Webhook Configuration

### Test Webhook in Stripe Dashboard

1. Go to your webhook endpoint in Stripe Dashboard
2. Click **"Send test webhook"**
3. Select event type: `checkout.session.completed`
4. Click **"Send test webhook"**
5. Check your application logs to see if webhook was received

### Check Webhook Logs

In Stripe Dashboard → Webhooks → Your endpoint → **"Recent events"**:
- ✅ Green checkmark = Successfully delivered
- ❌ Red X = Failed delivery

### Check Application Logs

Your Django application should log webhook events. Check your server logs when testing.

---

## Webhook Event Handling

Your webhook handler (`StripeWebhookView`) currently handles:

### 1. `checkout.session.completed`
- Updates payment status to `completed`
- Updates order status to `confirmed` and `paid`
- Sets `completed_at` timestamp

### 2. `payment_intent.succeeded`
- Updates payment status to `completed`
- Updates order status to `confirmed` and `paid`

### 3. `payment_intent.payment_failed`
- Updates payment status to `failed`
- Updates order payment_status to `failed`

---

## Security: Webhook Signature Verification

Your webhook handler automatically verifies webhook signatures using the `STRIPE_WEBHOOK_SECRET`. This ensures:

✅ Webhooks are actually from Stripe
✅ Webhooks haven't been tampered with
✅ Only legitimate payment events are processed

**Important:** Never skip signature verification in production!

---

## Troubleshooting

### Webhook Not Receiving Events

1. **Check webhook URL is correct** and accessible from internet
2. **Verify webhook secret** matches the one in Stripe Dashboard
3. **Check Stripe Dashboard** → Webhooks → Recent events for errors
4. **Ensure your server is running** and accessible
5. **Check firewall/security settings** allow incoming webhook requests

### Signature Verification Failed

1. **Verify webhook secret** matches exactly (no extra spaces)
2. **Check you're using correct secret** for test/live mode
3. **Ensure webhook endpoint** is receiving the `Stripe-Signature` header
4. **Check server logs** for specific error messages

### Webhook Received But Not Processing

1. **Check application logs** for errors
2. **Verify order_id** exists in metadata
3. **Check database** for payment/order records
4. **Test with Stripe Dashboard** → Send test webhook

---

## Current Configuration Summary

### Your Settings
```python
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='whsec_6BxRQHgIUXx3vr2qXA51w3gXBJV63uOI')
```

### Webhook Endpoint
```
POST /payments/webhook/
```

### Required Events
- `checkout.session.completed`
- `payment_intent.succeeded`
- `payment_intent.payment_failed`

---

## Quick Checklist

- [ ] Webhook URL configured in Stripe Dashboard
- [ ] Webhook secret copied and added to settings
- [ ] Required events selected (`checkout.session.completed`, etc.)
- [ ] Webhook endpoint accessible from internet (for production)
- [ ] Signature verification working (automatic in code)
- [ ] Test webhook sent successfully from Stripe Dashboard
- [ ] Application logs show webhook events being received

---

## Testing Webhook Locally

### Using Stripe CLI

```bash
# 1. Start Stripe CLI listener
stripe listen --forward-to localhost:8000/payments/webhook/

# 2. Copy the webhook secret shown (whsec_xxx)

# 3. Add to .env file
STRIPE_WEBHOOK_SECRET=whsec_xxx_from_cli

# 4. Trigger a test event
stripe trigger checkout.session.completed
```

### Using Stripe Dashboard

1. Go to Webhooks → Your endpoint
2. Click "Send test webhook"
3. Select `checkout.session.completed`
4. Click "Send test webhook"
5. Check your server logs

---

## Production Checklist

- [ ] Webhook URL uses HTTPS
- [ ] Webhook secret stored in environment variables (not hardcoded)
- [ ] Separate webhook endpoints for test and live mode
- [ ] Webhook events configured correctly
- [ ] Monitoring set up for webhook failures
- [ ] Error handling implemented
- [ ] Webhook logs reviewed regularly

---

## Support

If webhooks aren't working:

1. **Check Stripe Dashboard** → Webhooks → Recent events
2. **Review application logs** for errors
3. **Test with Stripe CLI** for local development
4. **Verify webhook secret** matches exactly
5. **Check server accessibility** from internet

---

*Your webhook is already configured in code - just make sure the URL and secret match what's in Stripe Dashboard!*

