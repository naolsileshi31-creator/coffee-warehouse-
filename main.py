import os
from fastapi import FastAPI
import uvicorn

# አፕሊኬሽኑን ማስጀመር
app = FastAPI(title="Coffee Warehouse Inventory")

# 1. Root route - የ404 ስህተቱን ያስተካክላል
@app.get("/")
def read_root():
    return {"message": "እንኳን ወደ ቡና ማከማቻው በደህና መጡ!"}

# 2. Example endpoint - "No operations defined" የሚለውን ስህተት ያስተካክላል
@app.get("/status")
def get_status():
    return {"status": "አፕሊኬሽኑ በትክክል እየሰራ ነው!"}

if __name__ == "__main__":
    # Render የሚፈልገውን ፖርት መጠቀም
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
