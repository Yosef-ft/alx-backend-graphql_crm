from celery import shared_task
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

@shared_task
def generate_crm_report():
    
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=True)
    client = Client(transport=transport, fetch_schema_from_transport=False)
    
    log_file_path = "/tmp/crm_report_log.txt"

    query = gql("""
        query CrmReportQuery {
          totalCustomers
          totalOrders
          allOrders {
            edges {
              node {
                totalAmount
              }
            }
          }
        }
    """)

    try:
        result = client.execute(query)

        customer_count = result.get('totalCustomers', 0)
        order_count = result.get('totalOrders', 0)
        
        total_revenue = sum(
            float(edge['node']['totalAmount']) for edge in result['allOrders']['edges']
        )

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_line = (
            f"{timestamp} - Report: {customer_count} customers, "
            f"{order_count} orders, {total_revenue:.2f} revenue.\n"
        )

        with open(log_file_path, 'a') as log_file:
            log_file.write(report_line)
        
        return f"Report generated successfully: {report_line.strip()}"

    except Exception as e:
        error_message = f"Failed to generate CRM report at {datetime.now()}: {e}\n"
        with open(log_file_path, 'a') as log_file:
            log_file.write(error_message)
        return error_message