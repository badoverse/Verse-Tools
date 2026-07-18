from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, IPvAnyAddress
from typing import Optional

app = FastAPI(title="Verse Tools API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_methods=["*"],
    allow_headers=["*"],
)


class NmapRequest(BaseModel):
    target: str           
    ports: Optional[str] = None   
    scan_type: str = "-sV"        


@app.post("/api/commands/nmap")
def generate_nmap_command(req: NmapRequest):
    if not req.target:
        raise HTTPException(status_code=400, detail="Target is required")

    parts = ["nmap", req.scan_type]
    if req.ports:
        parts += ["-p", req.ports]
    parts.append(req.target)

    return {"command": " ".join(parts)}