import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import uvicorn

# 1. Database Setup
DATABASE_URL = "sqlite:///./coffee_warehouse.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CoffeeBatch(Base):
    __tablename__ = "coffee_batches"
    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String, unique=True, index=True)
    coffee_type = Column(String)
    grade = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Coffee Warehouse Inventory")

# 2. HTML Frontend
HTML_CODE = """
<!DOCTYPE html>
<html lang="am">
<head><title>የቡና መጋዘን ክምችት</title></head>
<body style="font-family: sans-serif; padding: 20px;">
    <h1>☕ የቡና መጋዘ
