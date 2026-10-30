import pandas as pd
import numpy as np
from datetime import datetime

class KhataEngine:
    def __init__(self, customers_path, inventory_path, sales_path, payments_path):
        self.customers = pd.read_csv(customers_path)
        self.inventory = pd.read_csv(inventory_path)
        self.sales = pd.read_csv(sales_path)
        self.payments = pd.read_csv(payments_path)
        self._validate_data()

    def _validate_data(self):
        # Basic validation: Ensure critical columns are numeric
        self.sales['total_amount'] = pd.to_numeric(self.sales['total_amount'], errors='coerce').fillna(0)
        self.payments['amount_paid'] = pd.to_numeric(self.payments['amount_paid'], errors='coerce').fillna(0)
        self.inventory['current_stock'] = pd.to_numeric(self.inventory['current_stock'], errors='coerce').fillna(0)
        self.inventory['reorder_level'] = pd.to_numeric(self.inventory['reorder_level'], errors='coerce').fillna(0)

    def get_dashboard_metrics(self):
        total_sales = self.sales['total_amount'].sum()

        # Credit sales are those where payment_mode == 'Credit'
        credit_sales_df = self.sales[self.sales['payment_mode'] == 'Credit']
        total_outstanding_gross = credit_sales_df['total_amount'].sum()

        total_payments_received = self.payments['amount_paid'].sum()

        # Net outstanding = Gross Credit Sales - Payments Received
        net_outstanding = total_outstanding_gross - total_payments_received

        # Customers with balances
        customer_balances = self.get_customer_balances()
        customers_with_debt = customer_balances[customer_balances['balance'] > 0]
        num_debtors = len(customers_with_debt)

        # Low stock
        low_stock_df = self.inventory[self.inventory['current_stock'] <= self.inventory['reorder_level']]
        low_stock_count = len(low_stock_df)

        return {
            "total_sales": total_sales,
            "total_outstanding_gross": total_outstanding_gross,
            "total_payments_received": total_payments_received,
            "net_outstanding": net_outstanding,
            "num_debtors": num_debtors,
            "low_stock_count": low_stock_count,
            "top_debtors": customers_with_debt.sort_values(by='balance', ascending=False).head(5)
        }

    def get_customer_balances(self):
        # Sum of credit sales per customer
        credit_sales = self.sales[self.sales['payment_mode'] == 'Credit']
        sales_per_cust = credit_sales.groupby('customer_id')['total_amount'].sum().reset_index()
        sales_per_cust.columns = ['customer_id', 'total_credit']

        # Sum of payments per customer
        payments_per_cust = self.payments.groupby('customer_id')['amount_paid'].sum().reset_index()
        payments_per_cust.columns = ['customer_id', 'total_paid']

        # Merge
        balances = pd.merge(self.customers, sales_per_cust, on='customer_id', how='left')
        balances = pd.merge(balances, payments_per_cust, on='customer_id', how='left')

        balances = balances.fillna(0)
        balances['balance'] = balances['total_credit'] - balances['total_paid']

        return balances

    def get_inventory_status(self):
        df = self.inventory.copy()
        df['status'] = np.where(df['current_stock'] <= df['reorder_level'], 'Low Stock', 'OK')
        return df

    def get_transaction_history(self, customer_id):
        cust_sales = self.sales[self.sales['customer_id'] == customer_id]
        cust_payments = self.payments[self.payments['customer_id'] == customer_id]

        # Combine for a chronological view
        sales_view = cust_sales[['date', 'total_amount', 'payment_mode']].rename(columns={'total_amount': 'amount'})
        sales_view['type'] = 'Sale'

        pay_view = cust_payments[['date', 'amount_paid']].rename(columns={'amount_paid': 'amount'})
        pay_view['type'] = 'Payment'

        history = pd.concat([sales_view, pay_view]).sort_values(by='date')
        return history
