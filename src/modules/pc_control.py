import os
import re
import webbrowser
import subprocess
import pyautogui
import pyperclip
import time

pyautogui.FAILSAFE = True

EXCLUDED_APPS = (
    r"navegador|browser|chrome|firefox|edge|opera|brave|"
    r"explorador|archivos|directorio|carpeta|"
    r"terminal|consola|cmd|bash|"
    r"bloc\s*de\s*notas|notepad|editor|"
    r"youtube|yt|"
    r"proyecto|project"
)

EXCLUDED_APPS_PATTERN = EXCLUDED_APPS.replace(r"\s*", r"[\s_]*")

# ─── Mapa de proyectos locales ────────────────────
PROJECT_ROOTS = [
    os.path.expanduser("~/Proyectos"),
    os.path.expanduser("~/projects"),
    os.path.expanduser("~/Escritorio"),
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Documentos"),
    os.path.expanduser("~/Documents"),
]


def _build_project_map() -> dict[str, str]:
    pmap = {}
    seen = set()
    for root in PROJECT_ROOTS:
        if not os.path.isdir(root):
            continue
        try:
            for entry in os.listdir(root):
                full = os.path.join(root, entry)
                if not os.path.isdir(full):
                    continue
                key = entry.lower().replace(" ", "").replace("-", "").replace("_", "")
                if key not in seen:
                    seen.add(key)
                    pmap[key] = full
        except PermissionError:
            continue
    return pmap


PROJECT_MAP = _build_project_map()

# Alias manuales: nombre común → directorio real
PROJECT_ALIASES = {
    "atlas": PROJECT_MAP.get("jarvis"),
    "a.t.l.a.s": PROJECT_MAP.get("jarvis"),
    "jarvis": PROJECT_MAP.get("jarvis"),
}


COMMANDS = [
    # 1 — YouTube (abre + busca combinado)
    {
        "patterns": [
            r"(?:abre|abrir|abri|abrí)\s+(?:youtube|yt)\s+(?:y\s+)?(?:busca|buscar|buscá)\s+(.+?)$",
        ],
        "fn": "_search_youtube",
        "desc": "busca en YouTube",
    },
    # 2 — YouTube (solo abre)
    {
        "patterns": [
            r"(?:abre|abrir|abri|abrí)\s+(?:youtube|yt)$",
            r"(?:abre|abrir|abri|abrí)\s+(?:el\s+)?(?:youtube|yt)\s*$",
        ],
        "fn": "_open_youtube",
        "desc": "abre YouTube",
    },
    # 3 — Navegador específico
    {
        "patterns": [
            r"(?:abre|abrir|abri|abrí)\s+(?:el\s+)?(?:navegador|browser|chrome|firefox|edge|opera|brave)$",
            r"(?:abre|abrir|abri|abrí)\s+(?:chrome|firefox|edge|opera|brave)$",
        ],
        "fn": "_open_browser",
        "desc": "abre navegador",
    },
    # 4 — Explorador de archivos
    {
        "patterns": [
            r"(?:abre|abrir|abri|abrí)\s+(?:el\s+)?(?:explorador|archivos|directorio|carpeta|explorer)$",
        ],
        "fn": "_open_file_manager",
        "desc": "abre explorador de archivos",
    },
    # 5 — Terminal
    {
        "patterns": [
            r"(?:abre|abrir|abri|abrí)\s+(?:el\s+)?(?:terminal|consola|cmd|bash)$",
        ],
        "fn": "_open_terminal",
        "desc": "abre terminal",
    },
    # 6 — Bloc de notas / editor
    {
        "patterns": [
            r"(?:abre|abrir|abri|abrí)\s+(?:el\s+)?(?:bloc\s*de\s*notas|notepad|editor)$",
        ],
        "fn": "_open_notepad",
        "desc": "abre bloc de notas",
    },
    # 7 — Abrir proyecto local
    {
        "patterns": [
            r"(?:abre|abrir|abri|abrí)\s+(?:el\s+)?(?:proyecto|project)\s+(.+?)$",
            r"(?:abre|abrir|abri|abrí)\s+(.+?)\s+(?:en\s+)?(?:el\s+)?(?:proyecto|project)\s+(.+?)$",
        ],
        "fn": "_open_project",
        "desc": "abre proyecto local",
    },
    # 8 — Cualquier otra app
    {
        "patterns": [
            rf"(?:abre|abrir|abri|abrí)\s+(?:(?:el|la|un|una)\s+)?(?!{EXCLUDED_APPS_PATTERN})([\w\s\.áéíóúñüÁÉÍÓÚÑÜ]+?)$",
        ],
        "fn": "_open_app",
        "desc": "abre aplicación",
    },
    # 8 — Búsqueda en YouTube
    {
        "patterns": [
            r"(?:busca|buscar|buscá|pon|ponme|reproduce|pon\s*música)\s+(.+?)\s+(?:en\s+)?(?:youtube|yt)$",
            r"youtube\s+(.+?)$",
        ],
        "fn": "_search_youtube",
        "desc": "busca en YouTube",
    },
    # 9 — Búsqueda en Google
    {
        "patterns": [
            r"(?:busca|buscar|buscá|googlea|googlear)\s+(?:en\s+)?(?:internet|google|la\s*web)?\s*(.+?)$",
        ],
        "fn": "_search_google",
        "desc": "busca en Google",
    },
    # 10 — Escribir texto
    {
        "patterns": [
            r"(?:escribe|escribir|escribí|tipea|type|teclea|pon)\s+(.+?)$",
        ],
        "fn": "_type_text",
        "desc": "escribe texto",
    },
    # 11 — Presionar teclas
    {
        "patterns": [
            r"(?:presiona|presionar|pulsa|pulsar|tecla|atajo)\s+(.+?)$",
        ],
        "fn": "_press_keys",
        "desc": "presiona teclas",
    },
    # 12 — Cerrar ventana
    {
        "patterns": [
            r"(?:cierra|cerrar|cerrá|cerrame)\s+(todo|todas|todos|todito)",
            r"(?:cierra|cerrar|cerrá|cerrame)\s+(.+?)$",
            r"(?:cierra|cerrar|cerrá)\s+(?:la|el)\s+(?:ventana|app|programa|aplicación)$",
        ],
        "fn": "_close_window",
        "desc": "cierra ventana",
    },
    {
        "patterns": [
            r"(?:captura|capturar|saca|sacar)\s+(?:una\s+)?(?:captura|foto|screenshot|pantalla|pantallazo)",
            r"(?:toma|tomar)\s+(?:una\s+)?(?:captura|foto|screenshot|pantalla|pantallazo)",
        ],
        "fn": "_screenshot",
        "desc": "toma captura de pantalla",
    },
    {
        "patterns": [
            r"(?:desplázate|desplazar|scroll|baja|sube|desliza)\s+(?:hacia\s+)?(?:abajo|arriba)\s*(?:(\d+)\s*(?:veces|líneas|pixeles))?",
            r"(?:scroll)\s+(?:down|up)\s*(?:(\d+))?",
        ],
        "fn": "_scroll",
        "desc": "desplaza la página",
    },
    {
        "patterns": [
            r"(?:clic|click|cliquea|haz\s*clic|dale\s*clic|presiona)\s+(?:en\s+)?(.+?)$",
            r"(?:mueve|mover|mouse)\s+(?:el\s+)?(?:mouse|cursor|ratón)\s+(?:a|hasta|en)\s+(?:la\s+)?(?:posición|coordenadas)?\s*\(?(\d+)\s*[,\s]\s*(\d+)\)?",
        ],
        "fn": "_click",
        "desc": "hace clic",
    },
    {
        "patterns": [
            r"(?:minimiza|minimizar|minimizá|oculta|ocultar)\s+(.+?)$",
            r"(?:minimiza|minimizar|minimizá|oculta|ocultar)\s+(?:la\s+|el\s+)?(?:ventana|app|programa)",
        ],
        "fn": "_minimize_window",
        "desc": "minimiza ventana",
    },
    {
        "patterns": [
            r"(?:maximiza|maximizar|maximizá|agranda|agrandar|pantalla\s+completa)\s+(.+?)$",
        ],
        "fn": "_maximize_window",
        "desc": "maximiza ventana",
    },
]


def _normalize(text: str) -> str:
    return text.lower().strip()


def detect_command(text: str) -> tuple | None:
    text_norm = _normalize(text)
    for cmd in COMMANDS:
        for pattern in cmd["patterns"]:
            m = re.search(pattern, text_norm, re.IGNORECASE)
            if m:
                groups = m.groups()
                params = [g for g in groups if g is not None]
                return cmd["fn"], params
    return None


def execute_command(fn_name: str, params: list) -> str:
    fn = globals().get(fn_name)
    if fn:
        try:
            return fn(*params)
        except Exception as e:
            return f"Error al ejecutar: {e}"
    return "Comando no implementado"


# ─── Acciones ──────────────────────────────────────

BROWSER_CMD = {"chrome": "google-chrome", "firefox": "firefox", "edge": "msedge", "opera": "opera", "brave": "brave-browser"}


def _open_browser(*args):
    browser = args[0].strip() if args else None
    if browser:
        browser = _normalize(browser)
        for key, cmd in BROWSER_CMD.items():
            if key in browser or browser in key:
                subprocess.Popen([cmd])
                return f"Abriendo {key.capitalize()}..."
    webbrowser.open("https://www.google.com")
    return "Abriendo el navegador..."


def _open_file_manager(*args):
    subprocess.Popen(["xdg-open", "."])
    return "Abriendo explorador de archivos..."


def _open_terminal(*args):
    subprocess.Popen(["gnome-terminal"])
    return "Abriendo terminal..."


def _open_notepad(*args):
    subprocess.Popen(["gedit"])
    return "Abriendo bloc de notas..."


def _open_youtube(*args):
    webbrowser.open("https://www.youtube.com")
    return "Abriendo YouTube..."


def _open_project(*args):
    if not args:
        return "¿Qué proyecto quieres abrir?"

    # Case: "abre X en el proyecto Y" → args = (X, Y)
    if len(args) >= 2:
        sub, project = args[0].strip(), args[-1].strip()
        base = _find_project(project)
        if base:
            sub_path = os.path.join(base, sub)
            if os.path.exists(sub_path):
                subprocess.Popen(["xdg-open", sub_path])
                return f"Abriendo {sub} en {project}..."
            subprocess.Popen(["xdg-open", base])
            return f"'{sub}' no existe en {project}. Abriendo el proyecto..."
        return f"No encontré el proyecto '{project}'."

    # Case: "abre el proyecto X" → args = (X,)
    name = args[0].strip()
    path = _find_project(name)
    if path:
        subprocess.Popen(["xdg-open", path])
        return f"Abriendo proyecto '{os.path.basename(path)}'..."
    return f"No encontré el proyecto '{name}' en el PC."


def _find_project(name: str) -> str | None:
    key = name.lower().replace(" ", "").replace("-", "").replace("_", "")
    if key in PROJECT_ALIASES and PROJECT_ALIASES[key]:
        return PROJECT_ALIASES[key]
    if key in PROJECT_MAP:
        return PROJECT_MAP[key]
    for pkey, ppath in PROJECT_MAP.items():
        if key in pkey or pkey in key:
            return ppath
    return None


SITE_MAP = {
    "github": "https://github.com",
    "facebook": "https://facebook.com",
    "fb": "https://facebook.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "instagram": "https://instagram.com",
    "ig": "https://instagram.com",
    "linkedin": "https://linkedin.com",
    "gmail": "https://mail.google.com",
    "mail": "https://mail.google.com",
    "drive": "https://drive.google.com",
    "google drive": "https://drive.google.com",
    "docs": "https://docs.google.com",
    "google docs": "https://docs.google.com",
    "sheets": "https://sheets.google.com",
    "calendar": "https://calendar.google.com",
    "maps": "https://maps.google.com",
    "google maps": "https://maps.google.com",
    "youtube": "https://youtube.com",
    "yt": "https://youtube.com",
    "netflix": "https://netflix.com",
    "spotify": "https://open.spotify.com",
    "whatsapp": "https://web.whatsapp.com",
    "wa": "https://web.whatsapp.com",
    "chatgpt": "https://chatgpt.com",
    "gpt": "https://chatgpt.com",
    "claude": "https://claude.ai",
    "stackoverflow": "https://stackoverflow.com",
    "so": "https://stackoverflow.com",
    "reddit": "https://reddit.com",
    "wikipedia": "https://wikipedia.org",
    "wiki": "https://wikipedia.org",
    "amazon": "https://amazon.com",
    "ebay": "https://ebay.com",
    "aliexpress": "https://aliexpress.com",
    "a.t.l.a.s": "https://github.com/JUANRESTREPO95/A.T.L.A.S",
}


def _open_app(*args):
    name = args[0].strip() if args else ""
    if not name:
        return "¿Qué app quieres abrir?"
    clean = name.lower().strip().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    app_map = {
        "calculadora": "gnome-calculator",
        "calculos": "gnome-calculator",
        "calc": "gnome-calculator",
        "calendario": "gnome-calendar",
        "calend": "gnome-calendar",
        "musica": "spotify",
        "spotify": "spotify",
        "vscode": "code",
        "visual studio": "code",
        "visual studio code": "code",
        "code": "code",
        "discord": "discord",
        "slack": "slack",
        "whatsapp": "whatsapp-desktop",
        "telegram": "telegram-desktop",
        "steam": "steam",
        "obsidian": "obsidian",
        "notion": "notion",
        "postman": "postman",
        "docker": "docker",
        "configuracion": "gnome-control-center",
        "configuraciones": "gnome-control-center",
        "ajustes": "gnome-control-center",
    }

    # 1) Try app_map first
    app_cmd = app_map.get(clean)
    if app_cmd:
        try:
            subprocess.Popen([app_cmd])
            return f"Abriendo {name.capitalize()}..."
        except OSError:
            pass

    # 2) Check if it's a known website
    if clean in SITE_MAP:
        webbrowser.open(SITE_MAP[clean])
        return f"Abriendo {name.capitalize()} en el navegador..."

    # 3) Try as a system binary
    try:
        subprocess.run(["which", clean], capture_output=True, check=True)
        subprocess.Popen([clean])
        return f"Abriendo {name.capitalize()}..."
    except subprocess.CalledProcessError:
        pass

    # 4) Contiene "repositorio/repo" → abrir GitHub
    if "repositorio" in clean or "repo" in clean:
        repo_match = re.search(r"(?:repositorio|repo)\s+(.+)?", clean)
        repo_raw = repo_match.group(1) if repo_match else None
        if repo_raw:
            repo_clean = re.sub(r"\b(mi|mio|mia|mis|el|la|de|un|una)\b", "", repo_raw).strip()
            slug = repo_clean.replace(" ", "").upper()
            if "." in slug:
                url = f"https://github.com/JUANRESTREPO95/{slug}"
            else:
                url = f"https://github.com/search?q={repo_clean.replace(' ', '+')}&type=repositories"
        else:
            url = "https://github.com/JUANRESTREPO95"
        webbrowser.open(url)
        return f"Abriendo repositorio en GitHub..."

    # 5) Contiene puntos → abrir como URL
    if "." in clean:
        slug = clean.replace(" ", "")
        url = f"https://{slug}" if not slug.startswith("http") else slug
        webbrowser.open(url)
        return f"Abriendo {name}..."

    # 6) Fallback: sitio web genérico
    slug = clean.replace(" ", "")
    url = f"https://{slug}.com" if "." not in slug else f"https://{slug}"
    webbrowser.open(url)
    return f"No encontré {name.capitalize()} como app. Lo abrí como página web."


def _search_google(*args):
    query = args[0] if args else ""
    if not query:
        return "¿Qué quieres que busque?"
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Buscando '{query}' en Google..."


def _search_youtube(*args):
    query = args[0] if args else ""
    if not query:
        webbrowser.open("https://www.youtube.com")
        return "Abriendo YouTube..."
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Buscando '{query}' en YouTube..."


def _type_text(*args):
    text = args[0] if args else ""
    if not text:
        return "¿Qué texto quieres que escriba?"
    # Clean up the text - remove leading stop words
    for w in ["un", "una", "el", "la", "los", "las", "texto", "en", "la", "pantalla", "ahi", "allí"]:
        if text.lower().startswith(w + " "):
            text = text[len(w) + 1:]
            break
    pyautogui.write(text, interval=0.02)
    return f"Escribiendo: {text}"


def _press_keys(*args):
    combo = args[0] if args else ""
    if not combo:
        return "¿Qué teclas quieres que presione?"
    combo = combo.lower().strip()
    key_map = {
        "enter": "enter", "intro": "enter",
        "espacio": "space", "space": "space",
        "tab": "tab", "tabulador": "tab",
        "escape": "esc", "esc": "esc",
        "suprimir": "delete", "delete": "delete", "del": "delete",
        "control": "ctrl", "ctrl": "ctrl",
        "alt": "alt", "shift": "shift",
        "windows": "win", "win": "win", "super": "win",
        "flecha arriba": "up", "flecha abajo": "down",
        "flecha izquierda": "left", "flecha derecha": "right",
        "arriba": "up", "abajo": "down",
        "izquierda": "left", "derecha": "right",
        "f1": "f1", "f2": "f2", "f3": "f3", "f4": "f4",
        "f5": "f5", "f6": "f6", "f7": "f7", "f8": "f8",
        "f9": "f9", "f10": "f10", "f11": "f11", "f12": "f12",
    }

    combo = combo.replace(" + ", "+").replace(" mas ", "+").replace(" y ", "+")
    combo = re.sub(r"\s+", " ", combo)
    parts = re.split(r"\s*\+\s*|\s+", combo)
    parts = [p.strip().lower() for p in parts if p.strip()]
    keys = []
    for p in parts:
        p = p.strip()
        if len(p) == 1 and p.isalpha():
            keys.append(p.lower())
        else:
            keys.append(key_map.get(p, p))

    dangerous = [("alt", "f4"), ("ctrl", "w"), ("ctrl", "q"), ("ctrl", "f4")]
    if len(keys) > 1:
        for danger in dangerous:
            if all(dk in keys for dk in danger):
                if _is_atlas_window(_get_active_window_name()):
                    return "⚠️ No voy a presionar eso mientras ATLAS esté activo."

    if len(keys) == 1:
        pyautogui.press(keys[0])
    else:
        pyautogui.hotkey(*keys)
    return f"Presionando: {'+'.join(keys)}"


def _is_atlas_window(window_name: str) -> bool:
    return "atlas" in window_name.lower()


WMCTRL = subprocess.run(["which", "wmctrl"], capture_output=True).returncode == 0


def _get_active_window_name():
    try:
        r = subprocess.run(
            ["xprop", "-root", "_NET_ACTIVE_WINDOW"],
            capture_output=True, text=True, timeout=2
        )
        m = re.search(r"window id # (0x[0-9a-f]+)", r.stdout)
        if m:
            wid = m.group(1)
            r2 = subprocess.run(
                ["xprop", "-id", wid, "WM_NAME"],
                capture_output=True, text=True, timeout=2
            )
            m2 = re.search(r'WM_NAME\([^)]+\)\s*=\s*"(.+)"', r2.stdout)
            if m2:
                return m2.group(1)
        return ""
    except Exception:
        return ""


def _close_window(*args):
    raw = " ".join(args).lower() if args else ""
    is_close_all = "todo" in raw or "todas" in raw or "todos" in raw

    if is_close_all and WMCTRL:
        closed = 0
        try:
            r = subprocess.run(
                ["wmctrl", "-l"],
                capture_output=True, text=True, timeout=3
            )
            for line in r.stdout.strip().split("\n"):
                parts = line.split(None, 3)
                if len(parts) < 4:
                    continue
                wid, _, _, title = parts
                if _is_atlas_window(title):
                    continue
                subprocess.run(["wmctrl", "-ic", wid],
                               capture_output=True, timeout=2)
                closed += 1
                time.sleep(0.08)
        except Exception:
            return "No pude cerrar ventanas."
        return f"Cerradas {closed} ventana(s). ATLAS intacto."

    active_name = _get_active_window_name()
    if _is_atlas_window(active_name):
        return "⚠️ No voy a cerrar ATLAS. Pon otra ventana al frente primero."
    pyautogui.hotkey("alt", "f4")
    return "Cerrando ventana..."


def _minimize_window(*args):
    if _is_atlas_window(_get_active_window_name()):
        return "⚠️ No voy a minimizar ATLAS."
    pyautogui.hotkey("win", "d")
    return "Minimizando todas las ventanas..."


def _maximize_window(*args):
    pyautogui.hotkey("alt", "space")
    time.sleep(0.1)
    pyautogui.press("x")
    return "Maximizando ventana..."


def _screenshot(*args):
    path = os.path.join(os.path.expanduser("~"), "Escritorio", f"captura_{int(time.time())}.png")
    pyautogui.screenshot(path)
    return f"Captura guardada en {path}"


def _scroll(*args):
    direction = "down"
    amount = 1

    if args:
        raw = " ".join(args).lower()
        if "arriba" in raw or "up" in raw or "sub" in raw:
            direction = "up"
        m = re.search(r"(\d+)", raw)
        if m:
            amount = int(m.group(1))
    for _ in range(amount):
        if direction == "up":
            pyautogui.scroll(3)
        else:
            pyautogui.scroll(-3)
        time.sleep(0.05)
    msg = "arriba" if direction == "up" else "abajo"
    return f"Desplazando {msg} ({amount}x)"


def _click(*args):
    if args:
        raw = " ".join(args).lower()
        m = re.search(r"\(?\s*(\d+)\s*[,\s]\s*(\d+)\s*\)?", raw)
        if m:
            x, y = int(m.group(1)), int(m.group(2))
            pyautogui.click(x, y)
            return f"Clic en ({x}, {y})"
        for target in ["centro", "medio", "mitad"]:
            if target in raw:
                w, h = pyautogui.size()
                pyautogui.click(w // 2, h // 2)
                return "Clic en el centro de la pantalla"
    pyautogui.click()
    return "Clic realizado"


def process_message(message: str) -> tuple[bool, str]:
    cmd = detect_command(message)
    if cmd is None:
        return False, ""
    fn_name, params = cmd
    result = execute_command(fn_name, params)
    return True, result
