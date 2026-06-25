import datetime
import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import uvicorn

# 1. DATABASE SETUP
DATABASE_URL = "sqlite:///./coffee_warehouse.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CoffeeBatch(Base):
    __tablename__ = "coffee_batches"
    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String, unique=True, index=True, nullable=False)
    coffee_type = Column(String, default="Natural")
    grade = Column(String, nullable=False)
    origin = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

# 2. APP
app = FastAPI(title="Coffee Warehouse Inventory")

# 3. HTML TEMPLATE (እዚህ ላይ ነው ፎርሙ ያለው)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="am">
<head><title>የቡና መጋዘን ክምችት</title></head>
<body style="font-family: sans-serif; padding: 20px;">
    <h1>☕ የቡና መጋዘን ክምችት መቆጣጠሪያ</h1>
    <p>አፕሊኬሽኑ በተሳካ ሁኔታ ተገናኝቷል!</p>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_ui():
    return HTML_TEMPLATE

# Simple API Endpoint
@app.get("/status")
def get_status():
    return {"status": "እየሰራ ነው!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
