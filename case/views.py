import json
import requests
import lxml.html
import lxml.html.clean

from urllib.parse import urlparse
from uuid import uuid4

from django.shortcuts import render, redirect
from random import randrange

from django.urls import reverse
from scrapyd_api import ScrapydAPI

from case.models import ProductId, Product
from fabelio_app import settings


def page_one(request):
    rand = randrange(1000)
    if request.method == "POST":
        url = request.POST.get('input', None).strip()

        try:
            product_id = ProductId.objects.get(url=url)
            return redirect('page_three', uuid=product_id.uuid)
        except ProductId.DoesNotExist:
            domain = urlparse(url).netloc
            unique_id = str(uuid4())

            settings = {
                'unique_id': unique_id,
                'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
            }

            scrapyd = ScrapydAPI('http://localhost:6800')
            scrapyd.schedule('default', 'fab_crawler', settings=settings, url=url, domain=domain, uuid=unique_id)
            return redirect('page_three', uuid=unique_id)
    else:
        context = {'random_number': rand}

    return render(request, 'page_one.html', context)


def page_two(request):
    rand = randrange(1000)
    context = {'random_number': rand}
    products_list = Product.objects.values('name', 'image_src', 'last_update',
                                           'desc', 'pid__uuid', 'price')
    context['product_list'] = products_list

    return render(request, 'page_two.html', context)


def page_three(request, uuid):
    rand = randrange(1000)
    context = {'random_number': rand}
    try:
        product_id = ProductId.objects.get(uuid=uuid)

        response = requests.get(settings.FAB_PRODUCT_API.format(product_id.pid))
        response_data = json.loads(response.text)['product']
        desc = lxml.html.fromstring(response_data['description'])
        cleaner = lxml.html.clean.Cleaner(style=True)
        desc = cleaner.clean_html(desc)
        desc = desc.text_content()

        try:
            product = Product.objects.get(pid=product_id)
            product.price = response_data['unit_sale_price']
            product.save()
        except Product.DoesNotExist:
            product = Product()
            product.pid = product_id
            product.name = response_data['name']
            product.price = response_data['unit_sale_price']
            product.desc = desc
            product.image_src = response_data['product_image_url']
            product.save()

        context['product'] = {}
        context['product']['name'] = product.name
        context['product']['price'] = product.price
        context['product']['description'] = product.desc
        context['product']['image_url'] = product.image_src
    except ProductId.DoesNotExist:
        context['error_message'] = 'Product does not exist'

    return render(request, 'page_three.html', context)

