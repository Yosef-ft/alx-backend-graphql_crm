from django.db import models
from django.utils import timezone

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=15)


    def __str__(self):
        return f"Customer: {self.name}"



class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.FloatField()


    def __str__(self):
        return f"Product: {self.name}"



class Order(models.Model):
    customer_id = models.ForeignKey(to=Customer, on_delete=models.CASCADE)
    product_ids = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    order_date = models.DateTimeField(default=timezone.now())


    def __str__(self):
        return f"Order of: {self.customer_id.name}"
