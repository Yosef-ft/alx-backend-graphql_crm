import graphene
from graphene_django import DjangoObjectType

from crm.models import Customer, Product,  Order

class Query(graphene.ObjectType):
    hello: str = graphene.String(default_value="Hello, GraphQL!")


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ["name", "email", "phone"]


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ["name", "price", "stock"]


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ["customer_id", "customer_id", "order_date"]        

schema = graphene.Schema(query=Query)