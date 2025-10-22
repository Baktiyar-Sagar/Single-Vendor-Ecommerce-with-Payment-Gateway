import requests
import json
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def generate_sslcommerz_payment(request, order):

    post_body = {}
    post_body['store_id'] = settings.SSLCOMMERZ_STORE_ID
    post_body['store_passwd'] = settings.SSLCOMMERZ_STORE_PASSWORD
    post_body['total_amount'] = float(order.get_total_cost())
    post_body['currency' ] = 'BDT'
    post_body['tran_id'] = str(order.id)
    post_body['success_url'] = request.build_absolute_uri(f'/payment/success/{order.id}')
    post_body['fail_url'] = request.build_absolute_uri(f'/payment/fail/{order.id}')
    post_body['cancel_url'] = request.build_absolute_uri(f'/payment/cancel/{order.id}')
    post_body['cus_name' ] = f"{order. first_name} {order.last_name}",
    post_body['cus_email'] = order.email,
    post_body['cus_add1'] = order.address,
    post_body['cus_city'] = order.city,
    post_body['cus_postcode'] = order.postal_code,

    response = requests.post(settings.SSLCOMMERZ_PAYMENT_URL, data = post_body)
    return json.loads(response.text) # json -- > Python obj


def send_order_confirmation_email(order):
    subject = f'Order Confirmation - Order #{order.id}'
    message = render_to_string('html') # html code ---convert--- > string 
    to = order.email
    send_email = EmailMultiAlternatives(subject, '', to=[to])
    send_email.attach_alternative(message, 'text/html')
    send_email.send()

