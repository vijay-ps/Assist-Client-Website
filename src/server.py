from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import glob

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "outputs"

@app.get("/latest-response")
def get_latest_response():
    try:
        list_of_files = glob.glob(os.path.join(OUTPUT_DIR, "*.json"))
        
        if not list_of_files:
            return {"message": "No output files found", "data": ""}

        latest_file = max(list_of_files, key=os.path.getmtime)
        
        with open(latest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return {"filename": os.path.basename(latest_file), "data": data}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
