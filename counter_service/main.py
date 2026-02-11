from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# In-memory storage: user_id -> balance
balances_db: Dict[str, int] = {}

class Transaction(BaseModel):
    user_id: str
    amount: int

@app.post("/update_balance")
def update_balance(tx: Transaction):
    current = balances_db.get(tx.user_id, 0)
    balances_db[tx.user_id] = current + tx.amount
    return {"status": "ok", "new_balance": balances_db[tx.user_id]}

@app.get("/balance/{user_id}")
def get_balance(user_id: str):
    return {"balance": balances_db.get(user_id, 0)}

@app.get("/balances")
def get_all_balances():
    return balances_db