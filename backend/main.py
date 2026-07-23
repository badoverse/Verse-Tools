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

VALID_TIMING = {0, 1, 2, 3, 4, 5}


class NmapRequest(BaseModel):
    target: str
    ports: Optional[str] = None            # -p

    # Scan type (pick one primary technique)
    scan_type: str = "-sV"                 # -sS, -sT, -sU, -sV, -sn, -sA, -sW, -sM

    # Discovery / detection
    os_detection: bool = False             # -O
    version_detection: bool = False        # -sV (separate toggle, in case scan_type isn't -sV)
    version_intensity: Optional[int] = None  # --version-intensity (0-9)
    aggressive: bool = False               # -A (OS detect, version detect, script scan, traceroute)
    no_ping: bool = False                  # -Pn
    ping_only: bool = False                # -sn (host discovery only, no port scan)

    # Scripts
    default_scripts: bool = False          # -sC
    script: Optional[str] = None           # --script <name/category, comma-separated>
    script_args: Optional[str] = None      # --script-args

    # Port options
    all_ports: bool = False                # -p-
    top_ports: Optional[int] = None        # --top-ports <n>
    fast_scan: bool = False                # -F (fast, fewer ports)
    exclude_ports: Optional[str] = None    # --exclude-ports

    # Timing / performance
    timing: Optional[int] = None           # -T0 to -T5
    min_rate: Optional[int] = None         # --min-rate
    max_rate: Optional[int] = None         # --max-rate
    host_timeout: Optional[str] = None     # --host-timeout (e.g. 30s, 5m)

    # Evasion / spoofing
    fragment_packets: bool = False         # -f
    decoy: Optional[str] = None            # -D <decoy1,decoy2,ME,...>
    spoof_source_ip: Optional[str] = None  # -S
    spoof_mac: Optional[str] = None        # --spoof-mac
    source_port: Optional[int] = None      # -g / --source-port

    # IPv6
    ipv6: bool = False                     # -6

    # Output
    verbose: int = 0                       # -v (repeatable, 0 = none)
    output_normal: Optional[str] = None    # -oN <file>
    output_xml: Optional[str] = None       # -oX <file>
    output_grepable: Optional[str] = None  # -oG <file>
    output_all: Optional[str] = None       # -oA <basename> (writes -oN/-oX/-oG together)
    reason: bool = False                   # --reason
    open_only: bool = False                # --open

    # Misc
    exclude_hosts: Optional[str] = None    # --exclude
    interface: Optional[str] = None        # -e


@app.post("/api/commands/nmap")
def generate_nmap_command(req: NmapRequest):
    if not req.target:
        raise HTTPException(status_code=400, detail="Target is required")

    if req.timing is not None and req.timing not in VALID_TIMING:
        raise HTTPException(status_code=400, detail="Timing template must be between 0 and 5")
    if req.version_intensity is not None and not (0 <= req.version_intensity <= 9):
        raise HTTPException(status_code=400, detail="Version intensity must be between 0 and 9")

    parts = ["nmap"]

    # Scan type / discovery
    if req.ping_only:
        parts.append("-sn")
    else:
        if req.aggressive:
            parts.append("-A")
        else:
            parts.append(req.scan_type)
            if req.version_detection and req.scan_type != "-sV":
                parts.append("-sV")
            if req.os_detection:
                parts.append("-O")

        if req.default_scripts:
            parts.append("-sC")

    if req.no_ping:
        parts.append("-Pn")

    if req.version_intensity is not None:
        parts += ["--version-intensity", str(req.version_intensity)]

    if req.script:
        parts += ["--script", req.script]
    if req.script_args:
        parts += ["--script-args", req.script_args]

    # Ports
    if req.all_ports:
        parts.append("-p-")
    elif req.ports:
        parts += ["-p", req.ports]
    elif req.top_ports is not None:
        parts += ["--top-ports", str(req.top_ports)]
    elif req.fast_scan:
        parts.append("-F")

    if req.exclude_ports:
        parts += ["--exclude-ports", req.exclude_ports]

    # Timing / performance
    if req.timing is not None:
        parts.append(f"-T{req.timing}")
    if req.min_rate is not None:
        parts += ["--min-rate", str(req.min_rate)]
    if req.max_rate is not None:
        parts += ["--max-rate", str(req.max_rate)]
    if req.host_timeout:
        parts += ["--host-timeout", req.host_timeout]

    # Evasion
    if req.fragment_packets:
        parts.append("-f")
    if req.decoy:
        parts += ["-D", req.decoy]
    if req.spoof_source_ip:
        parts += ["-S", req.spoof_source_ip]
    if req.spoof_mac:
        parts += ["--spoof-mac", req.spoof_mac]
    if req.source_port is not None:
        parts += ["-g", str(req.source_port)]

    if req.ipv6:
        parts.append("-6")

    # Output
    if req.verbose > 0:
        parts.append("-" + "v" * min(req.verbose, 3))
    if req.reason:
        parts.append("--reason")
    if req.open_only:
        parts.append("--open")

    if req.output_all:
        parts += ["-oA", req.output_all]
    else:
        if req.output_normal:
            parts += ["-oN", req.output_normal]
        if req.output_xml:
            parts += ["-oX", req.output_xml]
        if req.output_grepable:
            parts += ["-oG", req.output_grepable]

    if req.exclude_hosts:
        parts += ["--exclude", req.exclude_hosts]
    if req.interface:
        parts += ["-e", req.interface]

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

# ---------------------------------------------------------------------------
# Hydra
# ---------------------------------------------------------------------------

VALID_OUTPUT_FORMATS = {"text", "json", "jsonv1"}


class HydraRequest(BaseModel):
    target: str
    service: str                          # ssh, ftp, http-get, http-post-form, etc.
    port: Optional[int] = None            # -s
    ssl: bool = False                     # -S

    # Credentials — either single values, wordlists, or a combo file
    login: Optional[str] = None           # -l
    login_list: Optional[str] = None      # -L file
    password: Optional[str] = None        # -p
    password_list: Optional[str] = None   # -P file
    combo_file: Optional[str] = None      # -C file (login:pass pairs, overrides -l/-L/-p/-P)

    # -e flags
    try_empty_password: bool = False      # -e n
    try_login_as_password: bool = False   # -e s
    try_reversed_login: bool = False      # -e r
    loop_around_users: bool = False       # -u

    # Performance
    tasks: Optional[int] = None           # -t
    wait_time: Optional[int] = None       # -w
    wait_time_per_thread: Optional[int] = None  # -W

    # Behaviour
    exit_on_first_found: bool = False           # -f
    exit_on_first_found_per_host: bool = False   # -F
    verbose: bool = False                 # -v
    debug: bool = False                   # -d
    quiet: bool = False                   # -q
    restore_session: bool = False         # -R
    ignore_restore_file: bool = False     # -I

    # Output
    output_file: Optional[str] = None     # -o
    output_format: Optional[str] = None   # -b

    # Module-specific extra args, e.g. http-post-form:
    # "/login:user=^USER^&pass=^PASS^:F=incorrect"
    module_options: Optional[str] = None


@app.post("/api/commands/hydra")
def generate_hydra_command(req: HydraRequest):
    if not req.target:
        raise HTTPException(status_code=400, detail="Target is required")
    if not req.service:
        raise HTTPException(status_code=400, detail="Service is required")

    if req.output_format and req.output_format not in VALID_OUTPUT_FORMATS:
        raise HTTPException(status_code=400, detail=f"Unsupported output format: {req.output_format}")

    if not req.combo_file:
        if not (req.login or req.login_list):
            raise HTTPException(status_code=400, detail="Provide a login (-l), login list (-L), or combo file (-C)")
        if not (req.password or req.password_list):
            raise HTTPException(status_code=400, detail="Provide a password (-p), password list (-P), or combo file (-C)")

    parts = ["hydra"]

    if req.combo_file:
        parts += ["-C", req.combo_file]
    else:
        if req.login:
            parts += ["-l", req.login]
        elif req.login_list:
            parts += ["-L", req.login_list]

        if req.password:
            parts += ["-p", req.password]
        elif req.password_list:
            parts += ["-P", req.password_list]

    e_flags = ""
    if req.try_empty_password:
        e_flags += "n"
    if req.try_login_as_password:
        e_flags += "s"
    if req.try_reversed_login:
        e_flags += "r"
    if e_flags:
        parts += ["-e", e_flags]

    if req.loop_around_users:
        parts.append("-u")

    if req.tasks is not None:
        parts += ["-t", str(req.tasks)]
    if req.wait_time is not None:
        parts += ["-w", str(req.wait_time)]
    if req.wait_time_per_thread is not None:
        parts += ["-W", str(req.wait_time_per_thread)]

    if req.exit_on_first_found:
        parts.append("-f")
    if req.exit_on_first_found_per_host:
        parts.append("-F")

    if req.verbose:
        parts.append("-v")
    if req.debug:
        parts.append("-d")
    if req.quiet:
        parts.append("-q")
    if req.restore_session:
        parts.append("-R")
    if req.ignore_restore_file:
        parts.append("-I")

    if req.output_file:
        parts += ["-o", req.output_file]
        if req.output_format:
            parts += ["-b", req.output_format]

    if req.ssl:
        parts.append("-S")
    if req.port is not None:
        parts += ["-s", str(req.port)]

    parts.append(req.target)
    parts.append(req.service)

    if req.module_options:
        parts.append(req.module_options)

    return {"command": " ".join(parts)}

# ---------------------------------------------------------------------------
# Sqlmap
# ---------------------------------------------------------------------------

VALID_LEVELS = {1, 2, 3, 4, 5}
VALID_RISKS = {1, 2, 3}
VALID_TECHNIQUES = set("BEUSTQ")  # Boolean, Error, Union, Stacked, Time, Inline


class SqlmapRequest(BaseModel):
    url: str
    data: Optional[str] = None            # --data (POST body)
    cookie: Optional[str] = None          # --cookie
    headers: Optional[List[str]] = None   # --header (repeatable)
    user_agent: Optional[str] = None      # --user-agent
    referer: Optional[str] = None         # --referer
    proxy: Optional[str] = None           # --proxy
    tor: bool = False                     # --tor
    random_agent: bool = False            # --random-agent

    method: Optional[str] = None          # --method (e.g. PUT)
    param_delimiter: Optional[str] = None # --param-del

    level: int = 1                        # --level (1-5)
    risk: int = 1                         # --risk (1-3)
    technique: Optional[str] = None       # --technique (subset of BEUSTQ)
    dbms: Optional[str] = None            # --dbms
    os: Optional[str] = None              # --os

    threads: Optional[int] = None         # --threads
    delay: Optional[float] = None         # --delay
    timeout: Optional[int] = None         # --timeout
    retries: Optional[int] = None         # --retries
    tamper: Optional[str] = None          # --tamper (comma-separated scripts)

    batch: bool = True                    # --batch (non-interactive, default on for safety of scripted use)
    random_agent_only: bool = False       # placeholder if you want to separate from random_agent later

    # Enumeration
    dbs: bool = False                     # --dbs
    current_db: bool = False              # --current-db
    current_user: bool = False            # --current-user
    is_dba: bool = False                  # --is-dba
    tables: bool = False                  # --tables
    columns: bool = False                 # --columns
    dump: bool = False                    # --dump
    dump_all: bool = False                # --dump-all
    db: Optional[str] = None              # -D <db>
    table: Optional[str] = None           # -T <table>
    columns_target: Optional[str] = None  # -C <col,col>

    # Access / exploitation
    os_shell: bool = False                # --os-shell
    sql_shell: bool = False               # --sql-shell
    file_read: Optional[str] = None       # --file-read
    file_write: Optional[str] = None      # --file-write
    file_dest: Optional[str] = None       # --file-dest

    # Output
    output_dir: Optional[str] = None      # --output-dir
    verbose_level: Optional[int] = None   # -v (0-6)


@app.post("/api/commands/sqlmap")
def generate_sqlmap_command(req: SqlmapRequest):
    if not req.url:
        raise HTTPException(status_code=400, detail="URL is required")

    if req.level not in VALID_LEVELS:
        raise HTTPException(status_code=400, detail="Level must be between 1 and 5")
    if req.risk not in VALID_RISKS:
        raise HTTPException(status_code=400, detail="Risk must be between 1 and 3")
    if req.technique:
        invalid = set(req.technique.upper()) - VALID_TECHNIQUES
        if invalid:
            raise HTTPException(status_code=400, detail=f"Invalid technique letters: {''.join(invalid)}")
    if req.verbose_level is not None and not (0 <= req.verbose_level <= 6):
        raise HTTPException(status_code=400, detail="Verbose level must be between 0 and 6")

    parts = ["sqlmap", "-u", req.url]

    if req.data:
        parts += ["--data", f"'{req.data}'"]
    if req.cookie:
        parts += ["--cookie", f'"{req.cookie}"']
    for header in req.headers or []:
        if header.strip():
            parts += ["--header", f'"{header.strip()}"']
    if req.user_agent:
        parts += ["--user-agent", f'"{req.user_agent}"']
    if req.referer:
        parts += ["--referer", f'"{req.referer}"']
    if req.random_agent:
        parts.append("--random-agent")

    if req.proxy:
        parts += ["--proxy", req.proxy]
    if req.tor:
        parts.append("--tor")

    if req.method:
        parts += ["--method", req.method.upper()]
    if req.param_delimiter:
        parts += ["--param-del", req.param_delimiter]

    if req.level != 1:
        parts += ["--level", str(req.level)]
    if req.risk != 1:
        parts += ["--risk", str(req.risk)]
    if req.technique:
        parts += ["--technique", req.technique.upper()]
    if req.dbms:
        parts += ["--dbms", req.dbms]
    if req.os:
        parts += ["--os", req.os]

    if req.threads is not None:
        parts += ["--threads", str(req.threads)]
    if req.delay is not None:
        parts += ["--delay", str(req.delay)]
    if req.timeout is not None:
        parts += ["--timeout", str(req.timeout)]
    if req.retries is not None:
        parts += ["--retries", str(req.retries)]
    if req.tamper:
        parts += ["--tamper", req.tamper]

    if req.batch:
        parts.append("--batch")

    # Enumeration — mutually informative, sqlmap allows combining these
    if req.dbs:
        parts.append("--dbs")
    if req.current_db:
        parts.append("--current-db")
    if req.current_user:
        parts.append("--current-user")
    if req.is_dba:
        parts.append("--is-dba")
    if req.tables:
        parts.append("--tables")
    if req.columns:
        parts.append("--columns")
    if req.dump:
        parts.append("--dump")
    if req.dump_all:
        parts.append("--dump-all")

    if req.db:
        parts += ["-D", req.db]
    if req.table:
        parts += ["-T", req.table]
    if req.columns_target:
        parts += ["-C", req.columns_target]

    if req.os_shell:
        parts.append("--os-shell")
    if req.sql_shell:
        parts.append("--sql-shell")
    if req.file_read:
        parts += ["--file-read", req.file_read]
    if req.file_write:
        parts += ["--file-write", req.file_write]
        if req.file_dest:
            parts += ["--file-dest", req.file_dest]

    if req.output_dir:
        parts += ["--output-dir", req.output_dir]
    if req.verbose_level is not None:
        parts += ["-v", str(req.verbose_level)]

    return {"command": " ".join(parts)}