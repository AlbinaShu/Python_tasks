from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, validator
from datetime import date
import re
import os
import json

app = FastAPI()

# Простой endpoint для проверки
@app.get("/")
def read_root():
    return {"message": "Hello World", "status": "Server is working!"}

@app.get("/test")
def test_endpoint():
    return {"test": "OK", "docs_url": "http://localhost:8000/docs"}

class Appeal(BaseModel):
    surname: str
    name: str
    birth_date: date
    phone: str
    email: EmailStr

    @validator('surname', 'name')
    def check_cyrillic_capital(cls, v):
        if not v:
            raise ValueError('Поле не может быть пустым')
        if not re.fullmatch(r'^[А-ЯЁ][а-яё]*$', v):
            raise ValueError('Только кириллица, первая буква заглавная')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if not v:
            raise ValueError('Номер телефона не может быть пустым')
        cleaned = re.sub(r'[\s\-\(\)]', '', v)
        if re.fullmatch(r'(\+7|8)9\d{9}', cleaned):
            return cleaned
        raise ValueError('Телефон должен быть в формате +79ХХХХХХХХХ или 89ХХХХХХХХХ')

DATA_FILE = "appeals.json"

def save_appeal(appeal: Appeal):
    data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    
    data.append(appeal.dict())
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.post("/appeal/")
async def submit_appeal(appeal: Appeal):
    try:
        save_appeal(appeal)
        return {
            "message": "Обращение сохранено",
            "data": appeal.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

