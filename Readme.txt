python -m venv .venv
pip install fastapi uvicorn
pip install python-dotenv
pip install groq
cd backend
uvicorn server:app --reload