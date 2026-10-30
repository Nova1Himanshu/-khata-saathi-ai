# KhataSaathi AI - Intelligent Retail Ledger Assistant

**Tagline:** From handwritten registers to intelligent business decisions.

Built for Hacktoberfest Hack Day 2026 at NIAT-VGU Jaipur.

## 🌟 Overview
KhataSaathi AI is an offline-first, AI-powered retail intelligence application designed for small Indian retailers. It transforms traditional ledger records into actionable business insights using Google's Gemma 4 model.

## 🚀 Key Features
- **Business Dashboard:** Real-time KPIs for sales, outstanding credit, and stock alerts.
- **Credit Intelligence:** Detailed tracking of customer debts with transaction-level evidence.
- **Inventory Management:** Automatic low-stock detection and restocking alerts.
- **AI Copilot:** A bilingual (Hindi/English) assistant powered by Gemma 4 to answer complex business questions.
- **Data Independence:** Local CSV-based storage ensuring privacy and offline capability.

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **Data Processing:** Pandas, NumPy
- **AI Engine:** Ollama + Gemma 4 (`gemma4:31b-cloud` or similar)
- **Language:** Python 3.x

## 📦 Installation & Setup

### Prerequisites
1. Install [Python 3.9+](https://www.python.org/)
2. Install [Ollama](https://ollama.com/)
3. Pull the Gemma 4 model:
   ```bash
   ollama pull gemma4:31b-cloud
   ```

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Nova1Himanshu/-khata-saathi-ai.git
   cd ./-khata-saathi-ai
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python generate_data.py
   streamlit run app/main.py
   ```

## 📊 Demo Script for Judges
1. **Launch:** Open the app and show the **Dashboard**.
2. **Insight:** Point out the "Net Outstanding" amount and "Low Stock Items".
3. **Deep Dive:** Go to **Customer Credit**, select a top debtor, and show their transaction history.
4. **AI Interaction (English):** Ask "Who owes the most money?" $\rightarrow$ AI identifies the top debtor.
5. **AI Interaction (Hindi):** Ask "Mere customers par kitna paisa pending hai?" $\rightarrow$ AI reports total net outstanding.
6. **Action:** Ask "Draft a polite payment reminder for Rajesh Kumar" $\rightarrow$ AI generates a professional draft.
7. **Inventory:** Show the **Inventory** page with highlighted low-stock items.

## 🛡️ Security & Reliability
- **Deterministic Calculations:** All financial math is performed by Pandas, not the LLM.
- **Privacy:** The configured cloud model may send business summaries and uploaded images to a remote provider. Do not use sensitive data without reviewing the model and provider settings.
- **Validation:** CSV imports are validated for numeric types to prevent crashes.

## 📝 Limitations
- Currently supports CSV imports only (Image-to-text OCR is experimental).
- Requires Ollama to be running locally for the AI Copilot to function.

**Current limitations:** OCR import is a prototype and does not save extracted transactions. CSV imports overwrite the local data files; back up your records first. The cloud model requires connectivity and may be unavailable.
