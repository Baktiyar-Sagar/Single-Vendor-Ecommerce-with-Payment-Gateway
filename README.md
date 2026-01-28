# Single Vendor Ecommerce with Payment Gateway

## Overview
A Django-based single-vendor e-commerce application with integrated payment gateway support. Provides product management, cart & checkout flow, order processing and basic admin interfaces.

## Features
- Product catalog (categories, product details)
- Shopping cart and checkout
- Order management and order history
- Payment gateway integration (sslcommerz)
- Admin dashboard for managing products and orders
- Basic user authentication (signup/login)
- Order confirmation emails (sent to customers after successful payment)
## Tech Stack
- Python, Django
- SQLite
- SSLCommerz
- HTML/CSS, optional JS for front-end interactions

## Environment Variables
Recommended to store sensitive values in a .env file:

- SSLCOMMERZ_STORE_ID
- SSLCOMMERZ_STORE_PASSWORD
- SSLCOMMERZ_PAYMENT_URL
- SSLCOMMERZ_VALIDATION_URL
- EMAIL_BACKEND
- EMAIL_HOST
- EMAIL_HOST_USER
- EMAIL_HOST_PASSWORD
- EMAIL_PORT
- EMAIL_USE_TLS

## Future Improvements
- Multi-vendor support and marketplace features
- Analytics, reporting and advanced order workflows
- Accessibility improvements
- Add AI chatbot to help with shopping and checkout
