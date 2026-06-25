import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
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
<html>
<head><title>የቡና መጋዘን</title></head>
<body>
    <h1>☕ የቡና መጋዘን ክምችት</h1>
    <form action="/batches" method="post">
        <input name="batch_number" placeholder="የባች ቁጥር" required>
        <input name="coffee_type" placeholder="የቡና አይነት" required>
        <input name="grade" placeholder="ደረጃ" required>
        <button type="submit">መዝግብ</button>
    </form>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_ui():
    return HTML_CODE

# 3. API Endpoints
@app.post("/batches")
def create_batch(batch_number: str, coffee_type: str, grade: str):
    db = SessionLocal()
    new_batch = CoffeeBatch(batch_number=batch_number, coffee_type=coffee_type, grade=grade)
    db.add(new_batch)
    db.commit()
    db.close()
    return {"message": "በስኬት ተመዝግቧል!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
