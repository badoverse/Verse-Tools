from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/dati")
def getData():
    return {"messaggio": "Dati da FastAPI"}

@app.get("/")
def home():
    return {"status": "Backend running"}

