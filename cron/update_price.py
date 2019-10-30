import os
import sys
import traceback

from django.core.wsgi import get_wsgi_application


sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fabelio_app.settings')
application = get_wsgi_application()

import json
import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from case.models import Product, ProductPriceHistory


def update_price():
    # take note start time
    d1 = timezone.localtime(timezone.now(), timezone.get_current_timezone())

    message = ''
    to_be_updated = []

    try:
        products_list = Product.objects.values('id', 'last_update', 'pid__pid')
        for product in products_list:
            if product['last_update'] < timezone.now() - timedelta(hours=1):
                to_be_updated.append(product)
    except Exception:
        traceback.print_exc()

    print('FOUND {} ITEMS TO BE UPDATED'.format(len(to_be_updated)))

    for product in to_be_updated:
        response = requests.get(settings.FAB_PRODUCT_API.format(product['pid__pid']))
        try:
            response_data = json.loads(response.text)['product']
            product = Product.objects.get(id=product['id'])
            product.price = response_data['unit_sale_price']
            product.save()

            price_history = ProductPriceHistory()
            price_history.product = product
            price_history.price = response_data['unit_sale_price']
            price_history.save()
        except Exception:
            traceback.print_exc()

    d2 = timezone.localtime(timezone.now(), timezone.get_current_timezone())

    # calculate delta time
    delta = d2 - d1

    # write the time to a file
    with open(settings.LOGS_DIRS + 'update_price.txt', 'a') as f:
        f.write('start: ' + str(d1) + '\n')
        f.write('to be updated: ' + str(to_be_updated) + '\n')
        f.write('message: ' + (message or 'Run successfully') + '\n')
        f.write('end  : ' + str(d2) + '\n')
        f.write('delta: ' + str(delta) + '\n')


update_price()
