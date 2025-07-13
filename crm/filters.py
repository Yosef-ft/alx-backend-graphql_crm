import django_filters
from django.db.models import Q
from .models import Customer, Product, Order


class OrderingFilter(django_filters.OrderingFilter):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('help_text', 'Sort results by field. Use comma-separated values. Prefix with - for descending order.')
        super().__init__(*args, **kwargs)


class CustomerFilter(django_filters.FilterSet):
    
    phone_pattern = django_filters.CharFilter(method='filter_by_phone_pattern', label="Phone Starts With")

    order_by = OrderingFilter(
        fields=(
            ('name', 'name'),
            ('email', 'email'),
            ('created_at', 'created_at'),
        )
    )

    class Meta:
        model = Customer
        fields = {
            'name': ['icontains'], 
            'email': ['icontains'],
            'created_at': ['gte', 'lte'], 
        }

    def filter_by_phone_pattern(self, queryset, name, value):
        
        return queryset.filter(phone__startswith=value)


class ProductFilter(django_filters.FilterSet):

    low_stock = django_filters.BooleanFilter(method='filter_low_stock', label="Low Stock (<10)")

    order_by = OrderingFilter(
        fields=(
            ('name', 'name'),
            ('price', 'price'),
            ('stock', 'stock'),
        )
    )

    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'price': ['gte', 'lte'], 
            'stock': ['exact', 'gte', 'lte'],
        }

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lt=10)        
        return queryset


class OrderFilter(django_filters.FilterSet):
    
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')

    product_id = django_filters.NumberFilter(field_name='products__id', distinct=True)

    order_by = OrderingFilter(
        fields=(
            ('total_amount', 'total_amount'),
            ('order_date', 'order_date'),
            ('customer__name', 'customer_name'),
        )
    )

    class Meta:
        model = Order
        fields = {
            'total_amount': ['gte', 'lte'],
            'order_date': ['gte', 'lte'],
        }