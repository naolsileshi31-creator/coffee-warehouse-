import datetime
import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import uvicorn

# 1. DATABASE SETUP
DATABASE_URL = "sqlite:///./coffee_warehouse.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. DATABASE MODELS
class CoffeeBatch(Base):
    __tablename__ = "coffee_batches"
    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String, unique=True, index=True, nullable=False)
    coffee_type = Column(String, default="Natural")
    grade = Column(String, nullable=False)
    origin = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Arrival(Base):
    __tablename__ = "arrivals"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("coffee_batches.id"), nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    number_of_bags = Column(Integer, nullable=False)
    total_weight_kg = Column(Float, nullable=False)
    supplier = Column(String, nullable=True)

class Dispatch(Base):
    __tablename__ = "dispatches"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("coffee_batches.id"), nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    number_of_bags = Column(Integer, nullable=False)
    total_weight_kg = Column(Float, nullable=False)
    destination = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

# 3. PYDANTIC SCHEMAS
class CoffeeBatchCreate(BaseModel):
    batch_number: str
    coffee_type: str = "Natural"
    grade: str
    origin: str

class CoffeeBatchResponse(CoffeeBatchCreate):
    id: int
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class ArrivalCreate(BaseModel):
    batch_id: int
    number_of_bags: int
    total_weight_kg: float
    supplier: Optional[str] = None

class ArrivalResponse(ArrivalCreate):
    id: int
    date: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class DispatchCreate(BaseModel):
    batch_id: int
    number_of_bags: int
    total_weight_kg: float
    destination: Optional[str] = None

class DispatchResponse(DispatchCreate):
    id: int
    date: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class StockStatusResponse(BaseModel):
    batch_id: int
    batch_number: str
    coffee_type: str
    grade: str
    origin: str
    total_bags_received: int
    total_weight_received: float
    total_bags_dispatched: int
    total_weight_dispatched: float
    current_bags_in_stock: int
    current_weight_in_stock: float

# 4. FASTAPI APPLICATION
app = FastAPI(title="Coffee Warehouse Inventory")

# --- FRONTEND UI (HTML/CSS/JS) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>የቡና መጋዘን ክምችት መቆጣጠሪያ</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body class="bg-gray-100 font-sans pb-10">
    <div class="bg-amber-800 text-white p-4 shadow-md text-center">
        <h1 class="text-xl font-bold">☕ የቡና መጋዘን ክምችት መቆጣጠሪያ (UI)</h1>
    </div>

    <div class="max-w-md mx-auto px-4 mt-6 space-y-6">
        
        <div class="bg-white p-5 rounded-xl shadow-sm">
            <h2 class="text-lg font-bold text-amber-950 mb-3">➕ አዲስ የቡና ባች መፍጠሪያ</h2>
            <div class="space-y-3">
                <input id="b_num" type="text" placeholder="የባች ቁጥር (ምሳሌ፡ BATCH-001)" class="w-full p-2 border rounded-md">
                <input id="b_type" type="text" value="Natural" placeholder="የቡና አይነት" class="w-full p-2 border rounded-md">
                <input id="b_grade" type="text" placeholder="ደረጃ (ምሳሌ፡ G1)" class="w-full p-2 border rounded-md">
                <input id="b_origin" type="text" placeholder="የቡና መነሻ ቦታ (ምሳሌ፡ Yirgacheffe)" class="w-full p-2 border rounded-md">
                <button onclick="createBatch()" class="w-full bg-amber-700 text-white p-2 rounded-md font-bold hover:bg-amber-800">ባች መዝግብ</button>
            </div>
        </div>

        <div class="bg-white p-5 rounded-xl shadow-sm">
            <h2 class="text-lg font-bold text-green-900 mb-3">📥 የቡና ገቢ (Arrival) መመዝገቢያ</h2>
            <div class="space-y-3">
                <input id="a_id" type="number" placeholder="የባች ID (ቁጥር ብቻ)" class="w-full p-2 border rounded-md">
                <input id="a_bags" type="number" placeholder="የስልቻ ብዛት" class="w-full p-2 border rounded-md">
                <input id="a_weight" type="number" placeholder="ጠቅላላ ክብደት (ኪ.ግ)" class="w-full p-2 border rounded-md">
                <input id="a_supplier" type="text" placeholder="አቅራቢ (Supplier)" class="w-full p-2 border rounded-md">
                <button onclick="recordArrival()" class="w-full bg-green-700 text-white p-2 rounded-md font-bold hover:bg-green-800">ገቢ መዝግብ</button>
            </div>
        </div>

        <div class="bg-white p-5 rounded-xl shadow-sm">
            <h2 class="text-lg font-bold text-blue-900 mb-3">📤 የቡና ወጪ (Dispatch) መመዝገቢያ</h2>
            <div class="space-y-3">
                <input id="d_id" type="number" placeholder="የባች ID (ቁጥር ብቻ)" class="w-full p-2 border rounded-md">
                <input id="d_bags" type="number" placeholder="የስልቻ ብዛት" class="w-full p-2 border rounded-md">
                <input id="d_weight" type="number" placeholder="ጠቅላላ ክብደት (ኪ.ግ)" class="w-full p-2 border rounded-md">
                <input id="d_dest" type="text" placeholder="መዳረሻ (Destination)" class="w-full p-2 border rounded-md">
                <button onclick="recordDispatch()" class="w-full bg-blue-700 text-white p-2 rounded-md font-bold hover:bg-blue-800">ወጪ መዝግብ</button>
            </div>
        </div>

        <div class="bg-white p-5 rounded-xl shadow-sm">
            <div class="flex justify-between items-center mb-3">
                <h2 class="text-lg font-bold text-gray-800">📊 አጠቃላይ የክምችት ሁኔታ (Stock)</h2>
                <button onclick="loadStock()" class="bg-gray-200 text-gray-700 px-3 py-1 text-sm rounded-md font-bold hover:bg-gray-300">🔄 አድስ</button>
            </div>
            
            <input id="search_input" type="text" oninput="filterStock()" placeholder="🔍 በባች ቁጥር ወይም በመነሻ ቦታ ፈልግ..." class="w-full p-2 border rounded-md mb-3 text-sm focus:outline-amber-700">

            <button onclick="downloadExcel()" class="w-full bg-emerald-600 text-white p-2 rounded-md font-bold mb-4 hover:bg-emerald-700 text-sm flex items-center justify-center gap-2">
                📊 ሙሉ ሪፖርት በExcel አውርድ
            </button>

            <div id="stock_list" class="space-y-3">
                <p class="text-gray-500 text-sm text-center">መረጃዎችን ለመጫን 'አድስ' የሚለውን ይጫኑ。</p>
            </div>
        </div>

    </div>

    <script>
        const API_URL = "";
        let allStockData = [];

        async function createBatch() {
            const data = {
                batch_number: document.getElementById('b_num').value,
                coffee_type: document.getElementById('b_type').value,
                grade: document.getElementById('b_grade').value,
                origin: document.getElementById('b_origin').value
            };
            const res = await fetch(API_URL + '/batches/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            if(res.ok) { alert('ባች በተሳካ ሁኔታ ተፈጥሯል!'); loadStock(); }
            else { alert('ስህተት'); }
        }

        async function recordArrival() {
            const data = {
                batch_id: parseInt(document.getElementById('a_id').value),
                number_of_bags: parseInt(document.getElementById('a_bags').value),
                total_weight_kg: parseFloat(document.getElementById('a_weight').value),
                supplier: document.getElementById('a_supplier').value
            };
            const res = await fetch(API_URL + '/arrivals/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            if(res.ok) { alert('የቡና ገቢ ተመዝግቧል!'); loadStock(); }
            else { alert('ስህተት'); }
        }

        async function recordDispatch() {
            const data = {
                batch_id: parseInt(document.getElementById('d_id').value),
                number_of_bags: parseInt(document.getElementById('d_bags').value),
                total_weight_kg: parseFloat(document.getElementById('d_weight').value),
                destination: document.getElementById('d_dest').value
            };
            const res = await fetch(API_URL + '/dispatches/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            if(res.ok) { alert('የቡና ወጪ ተመዝግቧል!'); loadStock(); }
            else { alert('ስህተት'); }
        }

        async function loadStock() {
            const res = await fetch(API_URL + '/stock/current');
            allStockData = await res.json();
            renderStock(allStockData);
        }

        function renderStock(data) {
            const container = document.getElementById('stock_list');
            container.innerHTML = "";
            if(data.length === 0) {
                container.innerHTML = "<p class='text-gray-500 text-sm text-center'>ምንም የተመዘገበ የቡና መረጃ አልተገኘም።</p>";
                return;
            }
            data.forEach(item => {
                container.innerHTML += `
                    <div class="border-l-4 border-amber-700 bg-amber-50 p-3 rounded-r-md text-sm">
                        <div class="font-bold text-gray-800 text-base">ባች ቁጥር: ${item.batch_number} (ID: ${item.batch_id})</div>
                        <div class="text-gray-600">አይነት: ${item.coffee_type} | ደረጃ: ${item.grade} | መነሻ: ${item.origin}</div>
                        <div class="grid grid-cols-2 gap-1 mt-2 text-xs font-semibold text-gray-700">
                            <div class="text-green-700">ገቢ ስልቻ: ${item.total_bags_received}</div>
                            <div class="text-blue-700">ወጪ ስልቻ: ${item.total_bags_dispatched}</div>
                            <div class="col-span-2 text-amber-900 border-t pt-1 mt-1 font-bold text-sm">
                                በአሁኑ ሰዓት መጋዘን ውስጥ ያለው ስቶክ: ${item.current_bags_in_stock} ስልቻ (${item.current_weight_in_stock} ኪ.ግ)
                            </div>
                        </div>
                    </div>
                `;
            });
        }

        function filterStock() {
            const query = document.getElementById('search_input').value.toLowerCase();
            const filtered = allStockData.filter(item => 
                item.batch_number.toLowerCase().includes(query) || 
                item.origin.toLowerCase().includes(query)
            );
            renderStock(filtered);
        }

        function downloadExcel() {
            if (allStockData.length === 0) {
                alert('የሚወርድ ምንም መረጃ የለም!');
                return;
            }
            let csvContent = "\uFEFF";
            csvContent += "Batch ID,Batch Number,Coffee Type,Grade,Origin,Total Bags Received,Total Weight (KG),Total Bags Dispatched,Total Weight Dispatched,Current Bags In Stock,Current Weight In Stock\n";
            allStockData.forEach(item => {
                let row = [
                    item.batch_id, `"${item.batch_number}"`, `"${item.coffee_type}"`, `"${item.grade}"`, `"${item.origin}"`,
                    item.total_bags_received, item.total_weight_received, item.total_bags_dispatched, item.total_weight_dispatched,
                    item.current_bags_in_stock, item.current_weight_in_stock
                ].join(",");
                csvContent += row + "\n";
            });
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement("a");
            link.setAttribute("href", URL.createObjectURL(blob));
            link.setAttribute("download", `የቡና_መጋዘን_ሪፖርት_${new Date().toISOString().slice(0,10)}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        window.onload = loadStock;
    </script>
</body>
</html>
