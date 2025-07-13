import graphene
import re
from graphene_django import DjangoObjectType
from django.db import transaction
from django.utils import timezone
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from graphene_django.filter import DjangoFilterConnectionField


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")
        interfaces = (graphene.relay.Node,)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")
        interfaces = (graphene.relay.Node,)

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")
        interfaces = (graphene.relay.Node,)

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(default_value=0)

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True, name="customerId")
    product_ids = graphene.List(graphene.NonNull(graphene.ID), required=True, name="productIds")
    order_date = graphene.DateTime(name="orderDate")

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        email = input.email
        phone = input.get('phone')

        if Customer.objects.filter(email=email).exists():
            raise Exception("A customer with this email already exists.")
        if phone and not re.match(r'^(\+1|1-)?\d{3}-?\d{3}-?\d{4}$', phone):
            raise Exception("Invalid phone number format.")

        customer_instance = Customer(
            name=input.name,
            email=email,
            phone=phone
        )
        customer_instance.save()

        return CreateCustomer(
            customer=customer_instance,
            message="Customer created successfully."
        )

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.NonNull(CustomerInput), required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        customers_to_create = []
        error_list = []
        emails_in_batch = set()

        for i, customer_data in enumerate(input):
            email = customer_data.email
            if Customer.objects.filter(email=email).exists() or email in emails_in_batch:
                error_list.append(f"Record {i}: Email '{email}' already exists.")
                continue

            customers_to_create.append(Customer(**customer_data))
            emails_in_batch.add(email)

        if customers_to_create:
            created_instances = Customer.objects.bulk_create(customers_to_create)
            return BulkCreateCustomers(customers=created_instances, errors=error_list)

        return BulkCreateCustomers(customers=[], errors=error_list)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, root, info, input):
        if input.price <= 0:
            raise Exception("Price must be a positive number.")
        if input.stock < 0:
            raise Exception("Stock cannot be a negative number.")

        product_instance = Product.objects.create(**input)
        return CreateProduct(product=product_instance)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    @classmethod
    def mutate(cls, root, info, input):
        try:
            customer_instance = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid Customer ID.")

        if not input.product_ids:
            raise Exception("You must select at least one product.")

        products_queryset = Product.objects.filter(pk__in=input.product_ids)
        if products_queryset.count() != len(input.product_ids):
            raise Exception("One or more invalid Product IDs were provided.")

        total = sum(p.price for p in products_queryset)

        order_instance = Order.objects.create(
            customer=customer_instance,
            total_amount=total,
            order_date=input.get('order_date') or timezone.now()
        )
        order_instance.products.set(products_queryset)

        return CreateOrder(order=order_instance)
    

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass

    updated_products = graphene.List(ProductType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products_list = []

        with transaction.atomic():
            for product in low_stock_products:
                product.stock += 10 
                product.save()
                updated_products_list.append(product)

        return UpdateLowStockProducts(
            updated_products=updated_products_list,
            message=f"Successfully updated stock for {len(updated_products_list)} products."
        )


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

class Query(graphene.ObjectType):
    node = graphene.Node.Field()
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    total_orders = graphene.Int()
    total_customers = graphene.Int()

    def resolve_total_customers(self, info, **kwargs):
        return Customer.objects.count()

    def resolve_total_orders(self, info, **kwargs):
        return Order.objects.count()