import json
import requests
import lxml.html
import lxml.html.clean

from urllib.parse import urlparse
from uuid import uuid4

from datetime import timedelta
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from random import randrange

from rest_framework import status
from scrapyd_api import ScrapydAPI

from case.models import ProductId, Product, ProductPriceHistory
from fabelio_app import settings


def page_one(request):
    rand = randrange(1000)
    context = {'random_number': rand}

    return render(request, 'page_one.html', context)


def page_two(request):
    rand = randrange(1000)
    context = {'random_number': rand}
    products_list = Product.objects.values('name', 'image_src', 'last_update',
                                           'desc', 'pid__pid', 'price')
    context['product_list'] = products_list

    return render(request, 'page_two.html', context)


def page_three(request, id):
    rand = randrange(1000)
    context = {'random_number': rand}
    try:
        product_id = ProductId.objects.get(pid=id)

        try:
            product = Product.objects.get(pid=product_id)

            if product.last_update < timezone.now() - timedelta(hours=1):
                response = requests.get(settings.FAB_PRODUCT_API.format(product_id.pid))
                response_data = json.loads(response.text)['product']

                product.price = response_data['unit_sale_price']
                product.save()

                price_history = ProductPriceHistory()
                price_history.product = product
                price_history.price = response_data['unit_sale_price']
                price_history.save()
        except Product.DoesNotExist:
            response = requests.get(settings.FAB_PRODUCT_API.format(product_id.pid))
            response_data = json.loads(response.text)['product']
            desc = lxml.html.fromstring(response_data['description'])
            cleaner = lxml.html.clean.Cleaner(style=True)
            desc = cleaner.clean_html(desc)
            desc = desc.text_content()

            product = Product()
            product.pid = product_id
            product.name = response_data['name']
            product.price = response_data['unit_sale_price']
            product.desc = desc
            product.image_src = response_data['product_image_url']
            product.save()

            price_history = ProductPriceHistory()
            price_history.product = product
            price_history.price = response_data['unit_sale_price']
            price_history.save()

        context['product'] = {}
        context['product']['name'] = product.name
        context['product']['price'] = product.price
        context['product']['description'] = product.desc
        context['product']['image_url'] = product.image_src

        product_history_list = ProductPriceHistory.objects.filter(product=product).order_by('-time_created')\
            .values('price', 'time_created')
        context['product_history_list'] = product_history_list
    except ProductId.DoesNotExist:
        context['error_message'] = 'Product does not exist'

    return render(request, 'page_three.html', context)


def url_check(request):
    url = request.POST.get('input', None).strip()

    try:
        product_id = ProductId.objects.get(url=url)

        return JsonResponse({'pid': product_id.pid, 'status': True}, status=status.HTTP_200_OK)
    except ProductId.DoesNotExist:
        domain = urlparse(url).netloc
        unique_id = str(uuid4())

        settings = {
            'unique_id': unique_id,
            'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }

        scrapyd = ScrapydAPI('http://localhost:6800')
        scrapyd.schedule('default', 'fab_crawler', settings=settings, url=url, domain=domain, uuid=unique_id)
    return JsonResponse({'status': False, 'uuid': unique_id}, status=status.HTTP_200_OK)


def get_pid(request):
    uuid = request.POST.get('uuid', None).strip()
    context = {}
    try:
        product_id = ProductId.objects.get(uuid=uuid)
        context['error_message'] = ''
        context['pid'] = product_id.pid
        return JsonResponse(context, status=status.HTTP_200_OK)
    except ProductId.DoesNotExist:
        context['error_message'] = 'Product ID does not exist'
        return JsonResponse(context, status=status.HTTP_404_NOT_FOUND)
