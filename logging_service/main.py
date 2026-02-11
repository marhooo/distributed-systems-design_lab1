from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# In-memory storage: UUID -> msg
messages_db: Dict[str, dict] = {}

class Message(BaseModel):
    uuid: str
    msg: dict

@app.post("/log")
def log_message(data: Message):
    messages_db[data.uuid] = data.msg
    print(f"Logged: {data.uuid}")
    return {"status": "ok"}

@app.get("/logs")
def get_logs():
    return list(messages_db.values())