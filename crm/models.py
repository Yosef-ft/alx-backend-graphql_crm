from django.db import models
from django.utils import timezone

class Customer(models.Model):
    # name: models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    # email: models.EmailField()
    email = models.EmailField(max_length=100)
    # phone: models.CharField(max_length=15)
    phone = models.CharField(max_length=15)


    def __str__(self):
        return self.name



class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.FloatField()


    def __str__(self):
        return f"Product: {self.name}"



class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    products = models.ManyToManyField(Product)
    order_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


    def __str__(self):
        return f"Order of: {self.customer.name}"
