import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import os
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

# 2. APP SETUP
app = FastAPI(title="Coffee Warehouse Inventory")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. ROUTES
@app.get("/", response_class=HTMLResponse)
def get_ui():
    return """
    <html>
        <body>
            <h1>እንኳን ወደ ቡና ማከማቻው በደህና መጡ!</h1>
            <p>አፕሊኬሽኑ በትክክል እየሰራ ነው።</p>
        </body>
    </html>
    """

@app.post("/batches")
def create_batch(batch_number: str, coffee_type: str, grade: str, origin: str, db: Session = Depends(get_db)):
    db_batch = CoffeeBatch(batch_number=batch_number, coffee_type=coffee_type, grade=grade, origin=origin)
    db.add(db_batch)
    db.commit()
    return {"message": "ባች ተመዝግቧል"}

@app.get("/stocks")
def get_stocks(db: Session = Depends(get_db)):
    return db.query(CoffeeBatch).all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
