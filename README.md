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

## 🚀 Quick Start (AI Setup)
1. Install Python and [Ollama](https://ollama.com/).
2. Prepare the configured model:
   ```bash
   ollama pull gemma4:31b-cloud
   ollama run gemma4:31b-cloud
   ```
   Sign in to Ollama if prompted. This cloud model requires internet access.
3. From the repository root, launch:
   ```bash
   pip install -r requirements.txt
   streamlit run app/main.py
   ```
   The app generates synthetic business data automatically when no ledger files exist.
   Existing partial datasets must be restored rather than overwritten.

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

**Current limitations:** OCR extraction requires human review before saving. Customers and products must already exist; reviewed OCR sales are recorded as credit. CSV imports overwrite the local data files; back up your records first. The cloud model requires connectivity and may be unavailable.
