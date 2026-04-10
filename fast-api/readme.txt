# Cài đặt
git clone https://github.com/kaztronaut1014/EduChatbot.git
python -m venv venv
pip install -r requirements.txt


#1 Chạy môi trường
    cd fast-api
    venv\Scripts\Activate.ps1

#2 chạy API
    uvicorn main:app --reload

#3 chạy frontend
    streamlit run frontend/app_ui.py

#4 import data
    python scripts/import_data.py