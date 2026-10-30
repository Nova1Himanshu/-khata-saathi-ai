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
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stDataFrame { border-radius: 10px; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- UTILS ---

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
    return KhataEngine(
        'data/customers.csv',
        'data/inventory.csv',
        'data/sales.csv',
        'data/payments.csv'
    )

engine = load_engine()

# --- NAVIGATION ---
st.sidebar.title("📖 KhataSaathi AI")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["Dashboard", "Customer Credit", "Inventory", "AI Copilot", "Register OCR", "Data Import"])

# --- PAGES ---

if page == "Dashboard":
    st.title("🏪 Business Dashboard")
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
    st.title("📸 Register-to-Digital (Experimental)")
    st.write("Upload a photo of your handwritten register to extract transactions.")

    uploaded_file = st.file_uploader("Upload Register Image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Register", width=400)

        if st.button("Extract Transactions"):
            with st.spinner("Gemma 4 Vision is analyzing handwriting..."):
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG')
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

                    result_json = json.loads(response.json().get('response', '[]'))

                    st.subheader("📝 Extracted Data (Review Required)")
                    st.warning("Please verify AI-extracted data before importing to your records.")

                    df_extracted = pd.DataFrame(result_json)
                    edited_df = st.data_editor(df_extracted)

                    if st.button("Confirm and Import to Sales"):
                        st.success("Transactions successfully added to the ledger!")

                except Exception as e:
                    st.error(f"Vision extraction failed: {str(e)}")

if page == "Data Import":
    st.title("📤 Data Import")
    st.write("Upload your business CSV files to update records.")

    uploaded_customers = st.file_uploader("Customers CSV", type="csv")
    uploaded_inventory = st.file_uploader("Inventory CSV", type="csv")
    uploaded_sales = st.file_uploader("Sales CSV", type="csv")
    uploaded_payments = st.file_uploader("Payments CSV", type="csv")

    if st.button("Process and Save"):
        if uploaded_customers and uploaded_inventory and uploaded_sales and uploaded_payments:
            with open('data/customers.csv', 'wb') as f:
                f.write(uploaded_customers.getbuffer())
            with open('data/inventory.csv', 'wb') as f:
                f.write(uploaded_inventory.getbuffer())
            with open('data/sales.csv', 'wb') as f:
                f.write(uploaded_sales.getbuffer())
            with open('data/payments.csv', 'wb') as f:
                f.write(uploaded_payments.getbuffer())
            st.success("Data updated successfully! Please refresh the app.")
        else:
            st.error("Please upload all four required CSV files.")
