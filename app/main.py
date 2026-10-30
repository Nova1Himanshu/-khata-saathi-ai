import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from engine import KhataEngine
import requests
import json
from PIL import Image
import io
import base64

# --- CONFIG ---
st.set_page_config(page_title="KhataSaathi AI", page_icon="📈", layout="wide")

# Custom CSS for professional look
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid var(--text-color);
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        color: var(--text-color);
    }
    .stDataFrame { border-radius: 10px; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- UTILS ---

def ensure_data_exists():
    import os
    from generate_data import generate_synthetic_data
    paths = [ROOT / 'data' / name for name in ['customers.csv', 'inventory.csv', 'sales.csv', 'payments.csv']]
    if not any(path.exists() for path in paths):
        (ROOT / 'data').mkdir(exist_ok=True)
        for path, frame in zip(paths, generate_synthetic_data()):
            frame.to_csv(path, index=False)
    elif not all(path.exists() for path in paths):
        raise ValueError('Some ledger files are missing. Restore all four CSV files; existing records will not be overwritten.')


def query_gemma(prompt, engine):
    metrics = engine.get_dashboard_metrics()
    balances = engine.get_customer_balances()
    inventory = engine.get_inventory_status()

    context = f"""
    Current Business State:
    - Total Sales: ₹{metrics['total_sales']}
    - Net Outstanding: ₹{metrics['net_outstanding']}
    - Low Stock Count: {metrics['low_stock_count']}
    - Top Debtors: {metrics['top_debtors'][['name', 'balance']].to_string(index=False)}
    - Inventory Alerts: {inventory[inventory['status'] == 'Low Stock'][['product_name', 'current_stock']].to_string(index=False)}
    """

    full_prompt = f"""
    You are KhataSaathi AI, a professional business assistant for an Indian shopkeeper.
    Use the provided business data to answer the user's question accurately.
    If the user asks in Hindi, answer in Hindi. If in English, answer in English.

    Business Data:
    {context}

    User Question: {prompt}

    Instructions:
    - Be polite and professional.
    - Use the provided numbers only. Do not invent figures.
    - If you can't find the answer in the data, say you don't know.
    - For payment reminders, draft a polite message.
    """

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma4:31b-cloud",
                "prompt": full_prompt,
                "stream": False
            },
            timeout=30
        )
        return response.json().get('response', "Sorry, I'm having trouble accessing the AI engine.")
    except Exception as e:
        return f"⚠️ AI Engine (Ollama) is unavailable. Please check if Ollama is running. Error: {str(e)}"

# --- DATA LOADING ---
@st.cache_resource
def load_engine():
    ensure_data_exists()
    return KhataEngine(
        ROOT / 'data' / 'customers.csv',
        ROOT / 'data' / 'inventory.csv',
        ROOT / 'data' / 'sales.csv',
        ROOT / 'data' / 'payments.csv'
    )

engine = load_engine()

# --- NAVIGATION ---
st.sidebar.title("📖 KhataSaathi AI")
st.sidebar.markdown("---")
def open_scanner():
    st.session_state.navigation = "Register OCR"

page = st.sidebar.radio("Navigation", ["Dashboard", "Customer Credit", "Inventory", "AI Copilot", "Register OCR", "Data Import"], key="navigation")

# --- PAGES ---

if page == "Dashboard":
    st.title("🏪 Business Dashboard")
    st.button("📸 Quick Scan Ledger", on_click=open_scanner, type="primary")
    metrics = engine.get_dashboard_metrics()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales", f"₹{metrics['total_sales']:,.2f}")
    col2.metric("Gross Credit", f"₹{metrics['total_outstanding_gross']:,.2f}", delta_color="inverse")
    col3.metric("Payments Received", f"₹{metrics['total_payments_received']:,.2f}")
    col4.metric("Net Outstanding", f"₹{metrics['net_outstanding']:,.2f}", delta=f"Pending", delta_color="inverse")

    st.markdown("---")
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("⚠️ Top Debtors")
        st.dataframe(metrics['top_debtors'][['name', 'balance']], use_container_width=True)

    with col_right:
        st.subheader("📦 Stock Alert")
        st.metric("Low Stock Items", metrics['low_stock_count'])
        if metrics['low_stock_count'] > 0:
            st.warning("Some products need immediate restocking!")

if page == "Customer Credit":
    st.title("👥 Customer Credit Intelligence")
    balances = engine.get_customer_balances()

    st.subheader("Outstanding Balances")
    st.dataframe(balances[['name', 'total_credit', 'total_paid', 'balance']], use_container_width=True)

    selected_cust = st.selectbox("Select Customer for Detailed History", balances['name'].tolist())
    if selected_cust:
        cust_id = balances[balances['name'] == selected_cust]['customer_id'].values[0]
        history = engine.get_transaction_history(cust_id)
        st.subheader(f"Transaction History for {selected_cust}")
        st.table(history)

if page == "Inventory":
    st.title("📦 Inventory Intelligence")
    inv = engine.get_inventory_status()

    # Highlight low stock
    def highlight_low_stock(s):
        return ['background-color: #ffcccc' if v == 'Low Stock' else '' for v in s]

    st.dataframe(inv.style.apply(highlight_low_stock, axis=1), use_container_width=True)

if page == "AI Copilot":
    st.title("🤖 Gemma 4 Business Copilot")
    st.info("Ask questions about your business in English or Hindi (e.g., 'Who owes the most money?' or 'Mere customers par kitna paisa pending hai?')")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask your business assistant..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing business records..."):
                response = query_gemma(prompt, engine)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

if page == "Register OCR":
    st.title("📸 Smart Register Scan")
    st.write("Upload a photo of your handwritten register to extract transactions.")

    source = st.radio("Image source", ["Upload photo", "Use camera"], horizontal=True)
    if source == "Use camera":
        uploaded_file = st.camera_input("Take a photo of your register")
    else:
        uploaded_file = st.file_uploader("Upload Register Image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Register", width=400)

        if st.button("Extract Transactions"):
            with st.spinner("Gemma 4 Vision is analyzing handwriting..."):
                img_byte_arr = io.BytesIO()
                image.convert('RGB').save(img_byte_arr, format='JPEG')
                img_bytes = img_byte_arr.getvalue()

                try:
                    img_b64 = base64.b64encode(img_bytes).decode('utf-8')

                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "gemma4:31b-cloud",
                            "prompt": "Analyze this image of a business ledger. Extract transactions into a JSON list. Fields: customer_name, product, quantity, amount, date. If handwriting is unclear, mark as 'unclear'.",
                            "images": [img_b64],
                            "stream": False,
                            "format": "json"
                        },
                        timeout=60
                    )

                    response.raise_for_status()
                    result_json = json.loads(response.json().get('response', '[]'))

                    st.session_state.ocr_rows = pd.DataFrame(result_json)
                except Exception as e:
                    st.error(f"Vision extraction failed: {str(e)}")

    if "ocr_rows" in st.session_state:
        try:
            st.subheader("📝 Extracted Data (Review Required)")
            st.warning("Please verify AI-extracted data before importing to your records.")
    
            edited_df = st.data_editor(st.session_state.ocr_rows)
    
            if st.button("Confirm and Import to Sales"):
                # Convert edited_df to the sales CSV format
                # Expected columns in sales.csv: transaction_id, date, customer_id, product_id, quantity, total_amount, payment_mode
    
                # We map the AI extracted fields to CSV columns
                import time
                sales_df = pd.read_csv(ROOT / 'data' / 'sales.csv')
    
                new_entries = []
                for _, row in edited_df.iterrows():
                    # Try to find customer_id by name
                    cust_df = pd.read_csv(ROOT / 'data' / 'customers.csv')
                    cust_match = cust_df[cust_df['name'] == row['customer_name']]
                    cid = int(cust_match['customer_id'].values[0]) if not cust_match.empty else None
    
                    # Try to find product_id by name
                    inv_df = pd.read_csv(ROOT / 'data' / 'inventory.csv')
                    prod_match = inv_df[inv_df['product_name'] == row['product']]
                    pid = int(prod_match['product_id'].values[0]) if not prod_match.empty else None
    
                    if cid is None or pid is None:
                        raise ValueError('Match every customer and product to an existing ledger entry before saving.')
                    quantity = float(row['quantity'])
                    amount = float(row['amount'])
                    if not np.isfinite(quantity) or not np.isfinite(amount) or quantity <= 0 or amount < 0:
                        raise ValueError('Quantity must be positive and amount must be nonnegative.')
                    pd.to_datetime(row['date'], errors='raise')
                    new_entries.append({
                        'transaction_id': int(time.time() * 1000) + len(sales_df) + len(new_entries),
                        'date': row['date'] if 'date' in row else datetime.now().strftime('%Y-%m-%d'),
                        'customer_id': cid,
                        'product_id': pid,
                        'quantity': quantity,
                        'total_amount': amount,
                        'payment_mode': 'Credit' # Default OCR to credit for review
                    })
    
                updated_sales = pd.concat([sales_df, pd.DataFrame(new_entries)], ignore_index=True)
                updated_sales.to_csv(ROOT / 'data' / 'sales.csv', index=False)
    
                st.success("Transactions successfully added to the ledger!")
                load_engine.clear()
                del st.session_state.ocr_rows
                st.rerun()
        except Exception as e:
            st.error(f"Import failed: {e}")

if page == "Data Import":
    st.title("📤 Data Import")
    st.write("Upload your business CSV files to update records.")

    uploaded_customers = st.file_uploader("Customers CSV", type="csv")
    uploaded_inventory = st.file_uploader("Inventory CSV", type="csv")
    uploaded_sales = st.file_uploader("Sales CSV", type="csv")
    uploaded_payments = st.file_uploader("Payments CSV", type="csv")

    if st.button("Process and Save"):
        if uploaded_customers and uploaded_inventory and uploaded_sales and uploaded_payments:
            with open(ROOT / 'data' / 'customers.csv', 'wb') as f:
                f.write(uploaded_customers.getbuffer())
            with open(ROOT / 'data' / 'inventory.csv', 'wb') as f:
                f.write(uploaded_inventory.getbuffer())
            with open(ROOT / 'data' / 'sales.csv', 'wb') as f:
                f.write(uploaded_sales.getbuffer())
            with open(ROOT / 'data' / 'payments.csv', 'wb') as f:
                f.write(uploaded_payments.getbuffer())
            load_engine.clear()
            st.success("Data updated successfully!")
        else:
            st.error("Please upload all four required CSV files.")
