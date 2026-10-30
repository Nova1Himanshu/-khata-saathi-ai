import pytest
import pandas as pd
import os
from app.engine import KhataEngine

# Use the synthetic data generated for tests
CUST_PATH = 'data/customers.csv'
INV_PATH = 'data/inventory.csv'
SALE_PATH = 'data/sales.csv'
PAY_PATH = 'data/payments.csv'

@pytest.fixture
def engine():
    return KhataEngine(CUST_PATH, INV_PATH, SALE_PATH, PAY_PATH)

def test_total_sales(engine):
    metrics = engine.get_dashboard_metrics()
    # Synthetic sales sum: 900+3000+450+2400+3000+1200+750 = 11700
    assert metrics['total_sales'] == 11700

def test_net_outstanding(engine):
    metrics = engine.get_dashboard_metrics()
    # Credit sales: 3000(Suresh)+450(Rajesh)+3000(Priya)+1200(Suresh) = 7650
    # Payments: 450(Rajesh)+1000(Suresh) = 1450
    # Net = 7650 - 1450 = 6200
    assert metrics['net_outstanding'] == 6200

def test_low_stock_detection(engine):
    metrics = engine.get_dashboard_metrics()
    # Steel Rods(10 <= 15), PVC Pipe(5 <= 10) = 2
    assert metrics['low_stock_count'] == 2

def test_customer_balance_calculation(engine):
    balances = engine.get_customer_balances()
    # Rajesh: Credit(450) - Paid(450) = 0
    rajesh_bal = balances[balances['name'] == 'Rajesh Kumar']['balance'].values[0]
    assert rajesh_bal == 0

    # Suresh: Credit(3000 + 1200) - Paid(1000) = 3200
    suresh_bal = balances[balances['name'] == 'Suresh Singh']['balance'].values[0]
    assert suresh_bal == 3200
