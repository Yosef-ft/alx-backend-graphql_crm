#!/bin/bash
# Cron job to clean inactive customers

cd /home/yosef/Documents/Programming/ALX/alx-backend-graphql_crm

source .venv/bin/activate

python manage.py shell <<EOF
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order
import logging

one_year_ago = timezone.now() - timedelta(days=365)

active_customer_ids = Order.objects.filter(order_date__gte=one_year_ago).values_list('customer_id', flat=True)

inactive_customers = Customer.objects.exclude(id__in=active_customer_ids)
count = inactive_customers.count()

inactive_customers.delete()

# Log result
timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
with open('/tmp/customer_cleanup_log.txt', 'a') as log_file:
    log_file.write(f"{timestamp} - Deleted {count} inactive customer(s)\n")
EOF
