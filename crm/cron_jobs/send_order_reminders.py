#!/bin/bash/env python3
import os
from datetime import datetime, timedelta

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
LOG_FILE_PATH = "/tmp/order_reminders_log.txt"

def send_reminders():
    """
    Queries for recent orders and logs them to a file.
    """

    transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT, verify=True, retries=3)
    client = Client(transport=transport, fetch_schema_from_transport=False)

    seven_days_ago = datetime.now() - timedelta(days=7)
    seven_days_ago_iso = seven_days_ago.isoformat()

    query_string = """
        query GetRecentOrders($sevenDaysAgo: DateTime!) {
          allOrders(orderDate_Gte: $sevenDaysAgo) {
            edges {
              node {
                id
                customer {
                  email
                }
              }
            }
          }
        }
    """
    query = gql(query_string)
    params = {"sevenDaysAgo": seven_days_ago_iso}

    try:
        result = client.execute(query, variable_values=params)
        
        with open(LOG_FILE_PATH, 'a') as log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_file.write(f"Processing reminders at {timestamp} \n")
            
            orders = result.get('allOrders', {}).get('edges', [])
            if not orders:
                log_file.write("No pending orders found.\n")
            
            for edge in orders:
                order_node = edge['node']
                order_id = order_node['id']
                customer_email = order_node['customer']['email']
                
                log_entry = f"REMINDER: Order ID {order_id} for customer {customer_email}\n"
                log_file.write(log_entry)
        
        print("Order reminders processed!")

    except Exception as e:
        with open(LOG_FILE_PATH, 'a') as log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_file.write(f"[{timestamp}] ERROR: Could not process reminders. Error: {e}\n")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    send_reminders()