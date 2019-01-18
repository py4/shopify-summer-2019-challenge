from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    title = models.CharField(max_length=30, null=False, blank=False, db_index=True)
    price = models.FloatField(null=False, blank=False, db_index=True)
    inventory_count = models.PositiveIntegerField(null=False, blank=False, db_index=True)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    complete = models.BooleanField(null=False, blank=False, default=False, db_index=True)


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(null=False, blank=False, db_index=True)
