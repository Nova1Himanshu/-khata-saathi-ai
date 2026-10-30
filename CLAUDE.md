# KhataSaathi AI Development Guide

## Tech Stack
- Streamlit UI; Pandas and CSV storage; Ollama with `gemma4:31b-cloud`.

## Project Structure
- `app/main.py`: UI, model requests, OCR review and CSV saving.
- `app/engine.py`: Deterministic ledger calculations.
- `generate_data.py`: Synthetic demo data generator.
- `data/`: Private local CSV store, excluded from Git.
- `tests/test_engine.py`: Ledger calculation tests.

## AI Integration
Business metrics are included in the prompt. This is context injection, with no vector database.
OCR flow: image → model JSON → editable review → customer/product matching and numeric validation → sales CSV.
OCR sales default to credit. Review all extracted values before confirming.
The cloud model sends prompts and images to the provider and requires connectivity.
CSV imports replace local records; back them up first.

## Run Commands
```bash
pip install -r requirements.txt
streamlit run app/main.py
```
Sample data is initialized on an empty first run.
For tests, install pytest, generate synthetic data in an isolated copy, and run `python -m pytest -q`.
Never commit real records, credentials, or environment files.
