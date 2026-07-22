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

# ---------------------------------------------------------------------------
# Gobuster
# ---------------------------------------------------------------------------

VALID_GOBUSTER_MODES = {"dir", "dns", "vhost", "fuzz"}


class GobusterRequest(BaseModel):
    mode: str = "dir"                      # dir | dns | vhost | fuzz
    url: Optional[str] = None              # -u (dir, vhost, fuzz - fuzz uses FUZZ keyword)
    domain: Optional[str] = None           # -d (dns mode)
    wordlist: str = "/usr/share/wordlists/dirb/common.txt"  # -w

    # General
    threads: Optional[int] = None          # -t
    timeout: Optional[str] = None          # --timeout (e.g. "10s")
    delay: Optional[str] = None            # --delay
    output_file: Optional[str] = None      # -o
    verbose: bool = False                  # -v
    quiet: bool = False                    # -q
    no_progress: bool = False              # -z
    no_error: bool = False                 # --no-error

    # Network
    proxy: Optional[str] = None            # --proxy
    insecure: bool = False                 # -k (--no-tls-validation)
    follow_redirect: bool = False          # -r
    user_agent: Optional[str] = None       # -a
    cookies: Optional[str] = None          # -c
    headers: Optional[List[str]] = None    # -H "Key: Value" (repeatable)
    basic_auth_user: Optional[str] = None  # -U
    basic_auth_pass: Optional[str] = None  # -P

    # dir mode
    extensions: Optional[str] = None       # -x (e.g. "php,html,txt")
    expanded: bool = False                 # -e
    add_slash: bool = False                # -f
    include_length: bool = False           # -l
    discover_backup: bool = False          # -d (dir mode: --discover-backup)
    status_codes: Optional[str] = None     # -s
    status_codes_blacklist: Optional[str] = None  # -b
    exclude_length: Optional[str] = None   # --exclude-length

    # dns mode
    show_ips: bool = False                 # -i
    show_cname: bool = False               # -c (conflicts with cookies flag -c, handled below)
    wildcard: bool = False                 # --wildcard
    resolver: Optional[str] = None         # -r (dns) - note: also conflicts with follow_redirect -r

    # vhost mode
    append_domain: bool = False            # --append-domain


@app.post("/api/commands/gobuster")
def generate_gobuster_command(req: GobusterRequest):
    mode = req.mode.lower()
    if mode not in VALID_GOBUSTER_MODES:
        raise HTTPException(status_code=400, detail=f"Unsupported mode: {req.mode}")

    if mode in ("dir", "vhost", "fuzz") and not req.url:
        raise HTTPException(status_code=400, detail="URL is required for this mode")
    if mode == "dns" and not req.domain:
        raise HTTPException(status_code=400, detail="Domain is required for dns mode")
    if not req.wordlist:
        raise HTTPException(status_code=400, detail="Wordlist is required")

    parts = ["gobuster", mode]

    if mode in ("dir", "vhost", "fuzz"):
        parts += ["-u", req.url]
    if mode == "dns":
        parts += ["-d", req.domain]

    parts += ["-w", req.wordlist]

    # General
    if req.threads is not None:
        parts += ["-t", str(req.threads)]
    if req.timeout:
        parts += ["--timeout", req.timeout]
    if req.delay:
        parts += ["--delay", req.delay]
    if req.verbose:
        parts.append("-v")
    if req.quiet:
        parts.append("-q")
    if req.no_progress:
        parts.append("-z")
    if req.no_error:
        parts.append("--no-error")

    # Network
    if req.proxy:
        parts += ["--proxy", req.proxy]
    if req.insecure:
        parts.append("-k")
    if req.user_agent:
        parts += ["-a", req.user_agent]
    if req.cookies:
        parts += ["-c", req.cookies]
    for header in req.headers or []:
        if header.strip():
            parts += ["-H", header.strip()]
    if req.basic_auth_user:
        parts += ["-U", req.basic_auth_user]
    if req.basic_auth_pass:
        parts += ["-P", req.basic_auth_pass]

    # Mode-specific
    if mode == "dir":
        if req.follow_redirect:
            parts.append("-r")
        if req.extensions:
            parts += ["-x", req.extensions]
        if req.expanded:
            parts.append("-e")
        if req.add_slash:
            parts.append("-f")
        if req.include_length:
            parts.append("-l")
        if req.discover_backup:
            parts.append("--discover-backup")
        if req.status_codes:
            parts += ["-s", req.status_codes]
        if req.status_codes_blacklist:
            parts += ["-b", req.status_codes_blacklist]
        if req.exclude_length:
            parts += ["--exclude-length", req.exclude_length]

    elif mode == "dns":
        if req.show_ips:
            parts.append("-i")
        if req.show_cname:
            parts.append("-c")  # note: overlaps with cookies -c in dns mode by design of gobuster
        if req.wildcard:
            parts.append("--wildcard")
        if req.resolver:
            parts += ["-r", req.resolver]

    elif mode == "vhost":
        if req.append_domain:
            parts.append("--append-domain")

    elif mode == "fuzz":
        if req.follow_redirect:
            parts.append("-r")

    if req.output_file:
        parts += ["-o", req.output_file]

    return {"command": " ".join(parts)}