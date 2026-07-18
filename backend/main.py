from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Verse Tools API")

# Allow your Vue dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Nmap
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Curl
# ---------------------------------------------------------------------------

VALID_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"}


class CurlRequest(BaseModel):
    url: str
    method: str = "GET"

    # Output
    output_file: Optional[str] = None     # -o <file>
    save_remote_name: bool = False        # -O

    # Behaviour flags
    follow_redirects: bool = False        # -L
    silent: bool = False                  # -s
    show_errors: bool = False             # -S (paired with silent -> -sS)
    verbose: bool = False                 # -v
    include_headers: bool = False         # -i
    insecure: bool = False                # -k
    compressed: bool = False              # --compressed

    # Identity / networking
    user_agent: Optional[str] = None      # -A
    referer: Optional[str] = None         # -e
    proxy: Optional[str] = None           # -x
    max_time: Optional[int] = None        # --max-time
    connect_timeout: Optional[int] = None # --connect-timeout

    # Auth
    basic_auth: Optional[str] = None      # -u user:pass
    bearer_token: Optional[str] = None    # -H "Authorization: Bearer <token>"

    # Headers
    headers: Optional[List[str]] = None   # each item -> -H "Key: Value"

    # Body
    data: Optional[str] = None            # -d
    data_is_json: bool = False            # adds Content-Type: application/json


@app.post("/api/commands/curl")
def generate_curl_command(req: CurlRequest):
    if not req.url:
        raise HTTPException(status_code=400, detail="URL is required")

    method = req.method.upper()
    if method not in VALID_METHODS:
        raise HTTPException(status_code=400, detail=f"Unsupported method: {req.method}")

    parts = ["curl"]

    if req.verbose:
        parts.append("-v")

    if req.silent:
        parts.append("-sS" if req.show_errors else "-s")

    if req.include_headers:
        parts.append("-i")

    if method == "HEAD":
        parts.append("-I")
    elif method != "GET":
        parts += ["-X", method]

    if req.follow_redirects:
        parts.append("-L")

    if req.insecure:
        parts.append("-k")

    if req.compressed:
        parts.append("--compressed")

    if req.user_agent:
        parts += ["-A", req.user_agent]

    if req.referer:
        parts += ["-e", req.referer]

    if req.proxy:
        parts += ["-x", req.proxy]

    if req.max_time is not None:
        parts += ["--max-time", str(req.max_time)]

    if req.connect_timeout is not None:
        parts += ["--connect-timeout", str(req.connect_timeout)]

    if req.basic_auth:
        parts += ["-u", req.basic_auth]

    if req.bearer_token:
        parts += ["-H", f"Authorization: Bearer {req.bearer_token}"]

    for header in req.headers or []:
        if header.strip():
            parts += ["-H", header.strip()]

    if req.data:
        if req.data_is_json:
            parts += ["-H", "Content-Type: application/json"]
            parts += ["-d", f"'{req.data}'"]
        else:
            parts += ["-d", req.data]

    if req.output_file:
        parts += ["-o", req.output_file]
    elif req.save_remote_name:
        parts.append("-O")

    parts.append(req.url)

    return {"command": " ".join(parts)}