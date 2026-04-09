#1 Chạy môi trường
    venv\Scripts\Activate.ps1

#2 chạy API
    uvicorn main:app --reload

#3 chạy frontend
    streamlit run frontend/app_ui.py

#4 import data
    python scripts/import_data.py