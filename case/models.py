from django.db import models


class ProductId(models.Model):
    pid = models.CharField(max_length=50)
    uuid = models.CharField(max_length=100)
    url = models.TextField()
    last_update = models.DateTimeField(auto_now=True)


class Product(models.Model):
    pid = models.ForeignKey(ProductId, on_delete=models.CASCADE)
    name = models.TextField(null=True)
    desc = models.TextField(null=True)
    image_src = models.TextField(null=True)
    price = models.CharField(max_length=50, null=True)
    last_update = models.DateTimeField(auto_now=True)


class ProductPriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.CharField(max_length=50, null=True)
    time_created = models.DateTimeField(auto_now=True)

