from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Verse Tools API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_methods=["*"],
    allow_headers=["*"],
)


def to_shell_multiline(segments: list[str]) -> str:
    """Join command segments into a multi-line string with ' \' line continuations.
    Hydra-only — every other tool stays single-line."""
    if not segments:
        return ""
    lines = [segments[0]] + [f"  {seg}" for seg in segments[1:]]
    return " \\\n".join(lines)


# ---------------------------------------------------------------------------
# Nmap
# ---------------------------------------------------------------------------

VALID_TIMING = {0, 1, 2, 3, 4, 5}


class NmapRequest(BaseModel):
    target: str
    ports: Optional[str] = None            # -p

    scan_type: str = "-sV"                 # -sS, -sT, -sU, -sV, -sn, -sA, -sW, -sM

    os_detection: bool = False             # -O
    version_detection: bool = False        # -sV (separate toggle)
    version_intensity: Optional[int] = None  # --version-intensity (0-9)
    aggressive: bool = False               # -A
    no_ping: bool = False                  # -Pn
    ping_only: bool = False                # -sn

    default_scripts: bool = False          # -sC
    script: Optional[str] = None           # --script
    script_args: Optional[str] = None      # --script-args

    all_ports: bool = False                # -p-
    top_ports: Optional[int] = None        # --top-ports
    fast_scan: bool = False                # -F
    exclude_ports: Optional[str] = None    # --exclude-ports

    timing: Optional[int] = None           # -T0 to -T5
    min_rate: Optional[int] = None         # --min-rate
    max_rate: Optional[int] = None         # --max-rate
    host_timeout: Optional[str] = None     # --host-timeout

    fragment_packets: bool = False         # -f
    decoy: Optional[str] = None            # -D <decoy1,decoy2,ME,...>
    spoof_source_ip: Optional[str] = None  # -S
    spoof_mac: Optional[str] = None        # --spoof-mac
    source_port: Optional[int] = None      # -g / --source-port

    ipv6: bool = False                     # -6

    verbose: int = 0                       # -v (repeatable, 0 = none)
    output_normal: Optional[str] = None    # -oN <file>
    output_xml: Optional[str] = None       # -oX <file>
    output_grepable: Optional[str] = None  # -oG <file>
    output_all: Optional[str] = None       # -oA <basename>
    reason: bool = False                   # --reason
    open_only: bool = False                # --open

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

    if req.timing is not None:
        parts.append(f"-T{req.timing}")
    if req.min_rate is not None:
        parts += ["--min-rate", str(req.min_rate)]
    if req.max_rate is not None:
        parts += ["--max-rate", str(req.max_rate)]
    if req.host_timeout:
        parts += ["--host-timeout", req.host_timeout]

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

    output_file: Optional[str] = None     # -o <file>
    save_remote_name: bool = False        # -O

    follow_redirects: bool = False        # -L
    silent: bool = False                  # -s
    show_errors: bool = False             # -S
    verbose: bool = False                 # -v
    include_headers: bool = False         # -i
    insecure: bool = False                # -k
    compressed: bool = False              # --compressed

    user_agent: Optional[str] = None      # -A
    referer: Optional[str] = None         # -e
    proxy: Optional[str] = None           # -x
    max_time: Optional[int] = None        # --max-time
    connect_timeout: Optional[int] = None # --connect-timeout

    basic_auth: Optional[str] = None      # -u user:pass
    bearer_token: Optional[str] = None    # -H "Authorization: Bearer <token>"

    headers: Optional[List[str]] = None   # -H "Key: Value"

    data: Optional[str] = None            # -d
    data_is_json: bool = False


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
    url: Optional[str] = None              # -u
    domain: Optional[str] = None           # -d (dns)
    wordlist: str = "/usr/share/wordlists/dirb/common.txt"

    threads: Optional[int] = None          # -t
    timeout: Optional[str] = None          # --timeout
    delay: Optional[str] = None            # --delay
    output_file: Optional[str] = None      # -o
    verbose: bool = False                  # -v
    quiet: bool = False                    # -q
    no_progress: bool = False              # -z
    no_error: bool = False                 # --no-error

    proxy: Optional[str] = None            # --proxy
    insecure: bool = False                 # -k
    follow_redirect: bool = False          # -r (dir/fuzz only)
    user_agent: Optional[str] = None       # -a
    cookies: Optional[str] = None          # -c (non-dns modes)
    headers: Optional[List[str]] = None    # -H
    basic_auth_user: Optional[str] = None  # -U
    basic_auth_pass: Optional[str] = None  # -P

    extensions: Optional[str] = None       # -x
    expanded: bool = False                 # -e
    add_slash: bool = False                # -f
    include_length: bool = False           # -l
    discover_backup: bool = False          # --discover-backup
    status_codes: Optional[str] = None     # -s
    status_codes_blacklist: Optional[str] = None  # -b
    exclude_length: Optional[str] = None   # --exclude-length

    show_ips: bool = False                 # -i
    show_cname: bool = False               # -c (dns: CNAME, not cookies)
    wildcard: bool = False                 # --wildcard
    resolver: Optional[str] = None         # -r (dns: resolver, not redirect)

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

    if req.proxy:
        parts += ["--proxy", req.proxy]
    if req.insecure:
        parts.append("-k")
    if req.user_agent:
        parts += ["-a", req.user_agent]
    for header in req.headers or []:
        if header.strip():
            parts += ["-H", header.strip()]
    if req.basic_auth_user:
        parts += ["-U", req.basic_auth_user]
    if req.basic_auth_pass:
        parts += ["-P", req.basic_auth_pass]

    if mode != "dns" and req.cookies:
        parts += ["-c", req.cookies]

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
            parts.append("-c")
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


class HydraExtraField(BaseModel):
    name: str
    value: str


class HydraRequest(BaseModel):
    target: str
    service: str
    port: Optional[int] = None            # -s
    ssl: bool = False                     # -S

    login: Optional[str] = None           # -l
    login_list: Optional[str] = None      # -L
    password: Optional[str] = None        # -p
    password_list: Optional[str] = None   # -P
    combo_file: Optional[str] = None      # -C

    try_empty_password: bool = False      # -e n
    try_login_as_password: bool = False   # -e s
    try_reversed_login: bool = False      # -e r
    loop_around_users: bool = False       # -u

    tasks: Optional[int] = None           # -t
    wait_time: Optional[int] = None       # -w
    wait_time_per_thread: Optional[int] = None  # -W

    exit_on_first_found: bool = False           # -f
    exit_on_first_found_per_host: bool = False   # -F
    verbose: bool = False                 # -v
    debug: bool = False                   # -d
    quiet: bool = False                   # -q
    restore_session: bool = False         # -R
    ignore_restore_file: bool = False     # -I

    output_file: Optional[str] = None     # -o
    output_format: Optional[str] = None   # -b

    # Structured form-module builder (http-post-form / https-post-form)
    form_path: Optional[str] = None                       # e.g. /login.php
    login_field: str = "username"                          # POST field receiving ^USER^
    password_field: str = "password"                       # POST field receiving ^PASS^
    extra_fields: Optional[List[HydraExtraField]] = None    # extra static POST fields
    condition_type: str = "F"                               # "F" (failure) or "S" (success)
    condition_string: Optional[str] = None

    # Escape hatch: raw override, used verbatim if provided
    module_options: Optional[str] = None


def _escape_hydra_field(value: str) -> str:
    """Hydra splits module options on ':' — literal colons must be escaped as '\\:'."""
    return value.replace(":", "\\:")


def build_http_form_module_options(req: HydraRequest) -> Optional[str]:
    if req.module_options:
        return req.module_options
    if not req.form_path:
        return None

    login_field = req.login_field or "username"
    password_field = req.password_field or "password"

    body_parts = [f"{login_field}=^USER^", f"{password_field}=^PASS^"]
    for field in req.extra_fields or []:
        if field.name.strip():
            body_parts.append(f"{field.name.strip()}={field.value.strip()}")
    body = "&".join(body_parts)

    condition = req.condition_string or ""
    condition_part = f"{req.condition_type}={condition}"

    path = _escape_hydra_field(req.form_path)
    body = _escape_hydra_field(body)
    condition_part = _escape_hydra_field(condition_part)

    return f"{path}:{body}:{condition_part}"


@app.post("/api/commands/hydra")
def generate_hydra_command(req: HydraRequest):
    if not req.target:
        raise HTTPException(status_code=400, detail="Target is required")
    if not req.service:
        raise HTTPException(status_code=400, detail="Service is required")
    if req.output_format and req.output_format not in VALID_OUTPUT_FORMATS:
        raise HTTPException(status_code=400, detail=f"Unsupported output format: {req.output_format}")

    is_form_service = req.service.endswith("-form")
    if is_form_service and not req.module_options and not req.form_path:
        raise HTTPException(status_code=400, detail="Form path is required for post-form services")
    if is_form_service and not req.module_options and not req.condition_string:
        raise HTTPException(status_code=400, detail="A success/failure condition string is required for post-form services")

    if not req.combo_file:
        if not (req.login or req.login_list):
            raise HTTPException(status_code=400, detail="Provide a login (-l), login list (-L), or combo file (-C)")
        if not (req.password or req.password_list):
            raise HTTPException(status_code=400, detail="Provide a password (-p), password list (-P), or combo file (-C)")

    segments = ["hydra"]

    if req.combo_file:
        segments.append(f"-C {req.combo_file}")
    else:
        if req.login:
            segments.append(f"-l {req.login}")
        elif req.login_list:
            segments.append(f"-L {req.login_list}")
        if req.password:
            segments.append(f"-p {req.password}")
        elif req.password_list:
            segments.append(f"-P {req.password_list}")

    e_flags = ""
    if req.try_empty_password:
        e_flags += "n"
    if req.try_login_as_password:
        e_flags += "s"
    if req.try_reversed_login:
        e_flags += "r"
    if e_flags:
        segments.append(f"-e {e_flags}")

    if req.loop_around_users:
        segments.append("-u")
    if req.tasks is not None:
        segments.append(f"-t {req.tasks}")
    if req.wait_time is not None:
        segments.append(f"-w {req.wait_time}")
    if req.wait_time_per_thread is not None:
        segments.append(f"-W {req.wait_time_per_thread}")
    if req.exit_on_first_found:
        segments.append("-f")
    if req.exit_on_first_found_per_host:
        segments.append("-F")
    if req.verbose:
        segments.append("-v")
    if req.debug:
        segments.append("-d")
    if req.quiet:
        segments.append("-q")
    if req.restore_session:
        segments.append("-R")
    if req.ignore_restore_file:
        segments.append("-I")

    if req.output_file:
        segments.append(f"-o {req.output_file}")
        if req.output_format:
            segments.append(f"-b {req.output_format}")

    if req.ssl:
        segments.append("-S")
    if req.port is not None:
        segments.append(f"-s {req.port}")

    segments.append(req.target)
    segments.append(req.service)

    if is_form_service:
        module_str = build_http_form_module_options(req)
        if module_str:
            segments.append(f'"{module_str}"')
    elif req.module_options:
        segments.append(req.module_options)

    return {"command": to_shell_multiline(segments)}


# ---------------------------------------------------------------------------
# Sqlmap
# ---------------------------------------------------------------------------

VALID_LEVELS = {1, 2, 3, 4, 5}
VALID_RISKS = {1, 2, 3}
VALID_TECHNIQUES = set("BEUSTQ")


class SqlmapRequest(BaseModel):
    url: str
    data: Optional[str] = None
    cookie: Optional[str] = None
    headers: Optional[List[str]] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    proxy: Optional[str] = None
    tor: bool = False
    random_agent: bool = False

    method: Optional[str] = None
    param_delimiter: Optional[str] = None

    level: int = 1
    risk: int = 1
    technique: Optional[str] = None
    dbms: Optional[str] = None
    os: Optional[str] = None

    threads: Optional[int] = None
    delay: Optional[float] = None
    timeout: Optional[int] = None
    retries: Optional[int] = None
    tamper: Optional[str] = None

    batch: bool = True

    dbs: bool = False
    current_db: bool = False
    current_user: bool = False
    is_dba: bool = False
    tables: bool = False
    columns: bool = False
    dump: bool = False
    dump_all: bool = False
    db: Optional[str] = None
    table: Optional[str] = None
    columns_target: Optional[str] = None

    os_shell: bool = False
    sql_shell: bool = False
    file_read: Optional[str] = None
    file_write: Optional[str] = None
    file_dest: Optional[str] = None

    output_dir: Optional[str] = None
    verbose_level: Optional[int] = None


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

# ---------------------------------------------------------------------------
# Nikto
# ---------------------------------------------------------------------------

VALID_FORMATS = {"csv", "json", "htm", "nbe", "sql", "txt", "xml"}
VALID_ASK_MODES = {"yes", "no", "auto"}


class NiktoRequest(BaseModel):
    target: str                            # -h / -host
    port: Optional[int] = None             # -p / -port
    ssl: bool = False                      # -ssl

    output_file: Optional[str] = None      # -o / -output
    output_format: Optional[str] = None    # -F / -Format

    tuning: Optional[str] = None           # -T / -Tuning (e.g. "1,2,3" or "x67")
    evasion: Optional[str] = None          # -evasion (1-8)

    basic_auth: Optional[str] = None       # -id <user:pass>
    root_path: Optional[str] = None        # -root
    cgi_dirs: Optional[str] = None         # -Cgidirs
    vhost: Optional[str] = None            # -vhost
    user_agent: Optional[str] = None       # -useragent
    proxy: Optional[str] = None            # -useproxy

    timeout: Optional[int] = None          # -timeout
    max_time: Optional[str] = None         # -maxtime (e.g. "1h", "30m")

    ask_mode: Optional[str] = None         # -ask (yes/no/auto)
    no_interactive: bool = False           # -nointeractive
    no_404: bool = False                   # -no404
    single_scan: bool = False              # -Single (single request per plugin test)

    plugins: Optional[str] = None          # -Plugins
    mutate: Optional[str] = None           # -mutate (1-6, comma-separated)
    mutate_options: Optional[str] = None   # -mutate-options

    display_options: Optional[str] = None  # -Display (e.g. "1,2,V")


@app.post("/api/commands/nikto")
def generate_nikto_command(req: NiktoRequest):
    if not req.target:
        raise HTTPException(status_code=400, detail="Target is required")

    if req.output_format and req.output_format not in VALID_FORMATS:
        raise HTTPException(status_code=400, detail=f"Unsupported output format: {req.output_format}")
    if req.output_format and not req.output_file:
        raise HTTPException(status_code=400, detail="Output format requires an output file")
    if req.ask_mode and req.ask_mode not in VALID_ASK_MODES:
        raise HTTPException(status_code=400, detail=f"Unsupported ask mode: {req.ask_mode}")

    parts = ["nikto", "-h", req.target]

    if req.port is not None:
        parts += ["-p", str(req.port)]
    if req.ssl:
        parts.append("-ssl")

    if req.output_file:
        parts += ["-o", req.output_file]
        if req.output_format:
            parts += ["-Format", req.output_format]

    if req.tuning:
        parts += ["-Tuning", req.tuning]
    if req.evasion:
        parts += ["-evasion", req.evasion]

    if req.basic_auth:
        parts += ["-id", req.basic_auth]
    if req.root_path:
        parts += ["-root", req.root_path]
    if req.cgi_dirs:
        parts += ["-Cgidirs", req.cgi_dirs]
    if req.vhost:
        parts += ["-vhost", req.vhost]
    if req.user_agent:
        parts += ["-useragent", f'"{req.user_agent}"']
    if req.proxy:
        parts += ["-useproxy", req.proxy]

    if req.timeout is not None:
        parts += ["-timeout", str(req.timeout)]
    if req.max_time:
        parts += ["-maxtime", req.max_time]

    if req.ask_mode:
        parts += ["-ask", req.ask_mode]
    if req.no_interactive:
        parts.append("-nointeractive")
    if req.no_404:
        parts.append("-no404")
    if req.single_scan:
        parts.append("-Single")

    if req.plugins:
        parts += ["-Plugins", req.plugins]
    if req.mutate:
        parts += ["-mutate", req.mutate]
    if req.mutate_options:
        parts += ["-mutate-options", req.mutate_options]

    if req.display_options:
        parts += ["-Display", req.display_options]

    return {"command": " ".join(parts)}