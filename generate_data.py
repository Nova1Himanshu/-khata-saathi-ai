from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

def generate_synthetic_data():
    # Customers
    customers = pd.DataFrame({
        'customer_id': [101, 102, 103, 104, 105],
        'name': ['Rajesh Kumar', 'Suresh Singh', 'Amit Sharma', 'Priya Patel', 'Vikram Mehra'],
        'phone': ['9876543210', '9876543211', '9876543212', '9876543213', '9876543214'],
        'address': ['Main Bazar', 'Station Road', 'Civil Lines', 'Market Area', 'Industrial Estate']
    })

    # Inventory
    inventory = pd.DataFrame({
        'product_id': [1, 2, 3, 4, 5],
        'product_name': ['Cement 50kg', 'Steel Rods 12mm', 'Paint White 10L', 'PVC Pipe 4in', 'Nails 1kg'],
        'unit_price': [450, 600, 1200, 300, 150],
        'current_stock': [50, 10, 25, 5, 100],
        'reorder_level': [20, 15, 10, 10, 20]
    })

    # Sales Transactions
    # Mixed cash and credit
    sales = pd.DataFrame({
        'transaction_id': [1001, 1002, 1003, 1004, 1005, 1006, 1007],
        'date': ['2026-10-01', '2026-10-02', '2026-10-05', '2026-10-10', '2026-10-15', '2026-10-20', '2026-10-25'],
        'customer_id': [101, 102, 101, 103, 104, 102, 105],
        'product_id': [1, 2, 1, 3, 4, 2, 5],
        'quantity': [2, 5, 1, 2, 10, 2, 5],
        'total_amount': [900, 3000, 450, 2400, 3000, 1200, 750],
        'payment_mode': ['Cash', 'Credit', 'Credit', 'Cash', 'Credit', 'Credit', 'Cash']
    })

    # Customer Payments (Against Credit)
    payments = pd.DataFrame({
        'payment_id': [2001, 2002],
        'date': ['2026-10-12', '2026-10-22'],
        'customer_id': [101, 102],
        'amount_paid': [450, 1000]
    })

    return customers, inventory, sales, payments

if __name__ == "__main__":
    Path("data").mkdir(exist_ok=True)
    c, i, s, p = generate_synthetic_data()
    c.to_csv('data/customers.csv', index=False)
    i.to_csv('data/inventory.csv', index=False)
    s.to_csv('data/sales.csv', index=False)
    p.to_csv('data/payments.csv', index=False)
    print("Synthetic data generated successfully.")
