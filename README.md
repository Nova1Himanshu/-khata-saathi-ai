# 📈 KhataSaathi AI — Intelligent Retail Ledger Assistant

**From handwritten registers to intelligent business decisions.**

## Overview
KhataSaathi AI helps small retailers understand sales, customer credit, payments, and inventory using a Streamlit dashboard and Gemma 4 through Ollama.

## Key Features
- **Smart Register Scan:** Capture a ledger photo using a camera or upload an image. Review and edit extracted transactions before saving them.
- **Business Dashboard:** Sales, outstanding credit, payments, and low-stock alerts.
- **Customer Credit:** Customer balances and transaction histories.
- **AI Copilot:** Ask business questions in Hindi or English using calculated ledger summaries.
- **Local CSV Storage:** Ledger calculations and storage work locally. The configured cloud AI requires internet and may send business summaries and images to the provider.
- **Automatic Demo Setup:** Synthetic records are generated when no ledger files exist. Partial existing datasets are preserved and require restoration.

## Quick Start
1. Install Python and [Ollama](https://ollama.com/).
2. Prepare the model:
   ```bash
   ollama pull gemma4:31b-cloud
   ollama run gemma4:31b-cloud
   ```
   Sign in if prompted and keep Ollama running.
3. Install dependencies from the repository root:
   ```bash
   pip install -r requirements.txt
   ```
4. Launch:
   ```bash
   streamlit run app/main.py
   ```
   Sample business data is created automatically on an empty first run. Allow camera access when prompted; camera availability depends on the browser and device.

## OCR Review and Limits
OCR is experimental. Verify every extracted field before confirming. Customers and products must match existing records; quantity must be positive and amount nonnegative. Saved OCR sales currently default to Credit. CSV imports replace existing files, so back up records first.

## Tests
In an isolated demo copy:
```bash
pip install pytest
python generate_data.py
python -m pytest -q
```
The generator replaces demo CSVs; do not run it over real shop records. Four ledger calculation tests pass. Live model responses and physical camera capture require further verification.

See [CLAUDE.md](CLAUDE.md) for the developer guide. Private CSVs, credentials, caches, and virtual environments are excluded from Git.
