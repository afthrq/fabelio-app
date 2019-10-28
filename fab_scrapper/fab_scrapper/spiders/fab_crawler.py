# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from case.models import ProductId


class FabCrawlerSpider(CrawlSpider):
    name = 'fab_crawler'
    product_id = None

    def __init__(self, *args, **kwargs):
        self.url = kwargs.get('url')
        self.domain = kwargs.get('domain')
        self.uuid = kwargs.get('uuid')
        self.start_urls = [self.url]
        self.allowed_domains = [self.domain]

        FabCrawlerSpider.rules = [
            Rule(LinkExtractor(unique=True), callback='parse_item'),
        ]
        super(FabCrawlerSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        product_info = response.css('div.product-info-main')

        if product_info is not None:
            self.product_id = response.css('div.price-box::attr(data-product-id)').get()

    def close(self, reason):
        if self.product_id is None:
            self.log('Getting product id failed')
        else:
            try:
                product_id = ProductId.objects.get(pid=self.product_id)
                product_id.uuid = self.uuid
                product_id.save()
            except ProductId.DoesNotExist:
                product_id = ProductId()
                product_id.pid = self.product_id
                product_id.uuid = self.uuid
                product_id.url = self.url
                product_id.save()
