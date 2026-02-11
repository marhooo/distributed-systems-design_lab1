import time
import uuid
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Адреси сервісів всередині мережі Docker
LOGGING_SERVICE_URL = "http://logging-service:8000"
COUNTER_SERVICE_URL = "http://counter-service:8000"

# Змінні для збереження часу (вимога з PDF)
stats = {
    "logging_time": 0.0,
    "counter_time": 0.0,
    "request_count": 0
}

class TransactionRequest(BaseModel):
    user_id: str
    amount: int

@app.post("/transaction")
async def process_transaction(tx: TransactionRequest):
    transaction_id = str(uuid.uuid4())
    
    async with httpx.AsyncClient() as client:
        # 1. Відправка в Logging Service
        start_log = time.time()
        try:
            await client.post(f"{LOGGING_SERVICE_URL}/log", json={
                "uuid": transaction_id,
                "msg": tx.dict()
            })
        except Exception as e:
            print(f"Logging failed: {e}")
        stats["logging_time"] += (time.time() - start_log)

        # 2. Відправка в Counter Service
        start_count = time.time()
        try:
            await client.post(f"{COUNTER_SERVICE_URL}/update_balance", json={
                "user_id": tx.user_id,
                "amount": tx.amount
            })
        except Exception as e:
            print(f"Counter failed: {e}")
        stats["counter_time"] += (time.time() - start_count)

    stats["request_count"] += 1
    return {"transaction_id": transaction_id}

@app.get("/user/{user_id}")
async def get_user_data(user_id: str):
    async with httpx.AsyncClient() as client:
        # Отримуємо баланс
        balance_resp = await client.get(f"{COUNTER_SERVICE_URL}/balance/{user_id}")
        balance = balance_resp.json().get("balance")
        
        # Отримуємо логи (в реальності треба фільтрувати по user_id, 
        # але згідно завдання logging повертає все, або треба допиляти)
        logs_resp = await client.get(f"{LOGGING_SERVICE_URL}/logs")
        all_logs = logs_resp.json()
        
        # Фільтруємо логи для юзера на рівні facade (спрощення)
        user_logs = [l for l in all_logs if l.get("user_id") == user_id]
        
        return {"balance": balance, "transactions": user_logs}

@app.get("/accounts")
async def get_accounts():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{COUNTER_SERVICE_URL}/balances")
        return resp.json()

@app.get("/stats")
def get_stats():
    return stats