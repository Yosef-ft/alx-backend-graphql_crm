from datetime import datetime
from crm.schema import UpdateLowStockProducts


LOG_FILE_PATH="/tmp/crm_heartbeat_log.txt"
LOG_FILE_PATH_STOCK="/tmp/low_stock_updates_log.txt"

def log_crm_heartbeat():

    with open(LOG_FILE_PATH, 'a') as log_file:
        timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        log_file.write(f"{timestamp} CRM is alive\n")


def update_low_stock():
    result = UpdateLowStockProducts().mutate(None, None)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE_PATH_STOCK, 'a') as f:
        f.write(f"{timestamp} - {result.message}\n")
        for product in result.updated_products:
            f.write(f"Updated: {product.name}, New Stock: {product.stock}\n")    