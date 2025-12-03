#!/bin/bash

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd backend/
uvicorn main:app --reload --port 8001 &
BACK_PID=$!

cd ../frontend/
python3 app.py &
FRONT_PID=$!

wait $BACK_PID $FRONT_PID
