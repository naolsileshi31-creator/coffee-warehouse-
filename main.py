import os
from fastapi import FastAPI, Form, Depends
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

# 2. HTML Frontend (የመመዝገቢያ ፎርም)
HTML_CODE = """
<!DOCTYPE html>
<html lang="am">
<head><title>የቡና መጋዘን ክምችት</title></head>
<body style="font-family: sans-serif; padding: 20px;">
    <h1>☕ የቡና መጋዘን ክምችት መቆጣጠሪያ</h1>
    <form action="/add" method="post">
        <input name="batch_number" placeholder="የባች ቁጥር" required><br><br>
        <input name="coffee_type" placeholder="የቡና አይነት" required><br><br>
        <input name="grade" placeholder="ደረጃ" required><br><br>
        <button type="submit">መዝግብ</button>
    </form>
    <h2>የተመዘገቡ ቡናዎች</h2>
    <a href="/stocks">ክምችቱን ይመልከቱ</a>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_ui():
    return HTML_CODE

@app.post("/add")
def add_batch(batch_number: str = Form(...), coffee_type: str = Form(...), grade: str = Form(...)):
    db = SessionLocal()
    new_batch = CoffeeBatch(batch_number=batch_number, coffee_type=coffee_type, grade=grade)
    db.add(new_batch)
    db.commit()
    db.close()
    return {"message": "በስኬት ተመዝግቧል!", "back": "ወደ ዋናው ገጽ ለመመለስ ወደ ኋላ ይሂዱ"}

@app.get("/stocks")
def get_stocks():
    db = SessionLocal()
    items = db.query(CoffeeBatch).all()
    db.close()
    return items

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
