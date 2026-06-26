import customtkinter as ctk
from tkinter import messagebox, Canvas
import os, math, random, threading, json
from dotenv import load_dotenv, set_key
from datetime import datetime
import psutil
import requests
from src.core.ollama_client import OllamaClient
from src.modules.web_search import search_web
from src.modules.pc_control import process_message

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
ENV_PATH = os.path.join(BASE_DIR, ".env")
SOUL_PATH = os.path.join(BASE_DIR, "soul.md")
MEMORY_PATH = os.path.join(BASE_DIR, "memoria.json")
BG_COLOR = "#06080f"
PANEL_COLOR = "#0b0f1a"
BORDER_COLOR = "#1a2a44"
ACCENT = "#00bbff"
ACCENT_DIM = "#006688"
TEXT_DIM = "#7799bb"
TEXT_BRIGHT = "#cceeff"

FONT_XS = 10
FONT_SM = 11
FONT_MD = 13
FONT_LG = 16
FONT_XL = 20
FONT_XXL = 28

LANG = {
    "es": {
        "window_title": "ATLAS - Asistente Personal",
        "online": "Online",
        "inactive": "Inactivo",
        "listening": "Escuchando palabra de activación...",
        "type_msg": "Escribe un mensaje...",
        "conversation": "Conversación",
        "welcome_msg": "Hola, soy ATLAS.\nEl backend está desconectado.\nAlgunas funciones pueden estar limitadas.\n¿Cómo puedo ayudarte hoy?",
        "sys_stats": "Estadísticas del Sistema",
        "cpu_usage": "Uso de CPU",
        "ram_usage": "Uso de RAM",
        "disk": "Disco",
        "weather": "Clima",
        "camera": "Cámara",
        "camera_inactive": "La cámara está inactiva. Haz clic en el botón de encendido para iniciar.",
        "sys_uptime": "Tiempo Activo",
        "running_for": "Sistema funcionando por:",
        "session": "Sesión",
        "commands": "Comandos",
        "sys_load": "Carga del Sistema",
        "moderate": "Moderada",
        "humidity": "Humedad",
        "wind": "Viento",
        "feels": "Sensación",
        "city_not_set": "Ciudad no configurada",
        "config_title": "Configuración",
        "tab_clima": "Clima",
        "tab_api": "API + Modelo",
        "tab_general": "General",
        "clima_search": "Buscar ciudad para el clima:",
        "clima_example": "Ej: medellin, london, queretaro, tokyo",
        "clima_search_btn": "Buscar",
        "clima_save_btn": "Guardar ciudad mostrada",
        "clima_preview": "Resumen del clima",
        "clima_city": "Ciudad:",
        "clima_temp": "Temperatura:",
        "clima_desc": "Estado:",
        "clima_hum": "Humedad:",
        "clima_wind": "Viento:",
        "clima_feel": "Sensación térmica:",
        "api_key_label": "API Key de Ollama Cloud:",
        "api_key_hint": "Tu API key de Ollama Cloud para conectar el asistente",
        "model_label": "Modelo de IA:",
        "model_hint": "Modelo que usará ATLAS para responder",
        "temp_label": "Temperatura (0.0 - 1.0):",
        "temp_hint": "Controla la creatividad del modelo (más alto = más creativo)",
        "save_api_btn": "Guardar API + Modelo",
        "gen_label": "Configuración general",
        "gen_hint": "Aquí aparecerán más opciones generales en futuras actualizaciones.",
        "lang_label": "Idioma / Language:",
        "save_all_btn": "Guardar todo",
        "close_btn": "Cerrar",
        "searching": "Buscando...",
        "no_results": "No se encontraron ciudades",
        "loading_weather": "Cargando clima...",
        "weather_error": "Error al obtener clima",
        "conn_error": "Error de conexión",
        "save_city_first": "Primero busca y selecciona una ciudad.",
        "city_saved": "Ciudad guardada:",
        "enter_city": "Escribe el nombre de una ciudad.",
        "api_empty_warn": "La API Key no puede estar vacía.",
        "api_saved": "API Key, modelo y temperatura guardados.",
        "all_saved": "Toda la configuración guardada.",
        "lang_saved": "Idioma cambiado a",
        "system_stats": "Estadísticas del Sistema",
        "cpu_box": "CPU",
        "mem_box": "Memoria",
    },
    "en": {
        "window_title": "ATLAS - Personal Assistant",
        "online": "Online",
        "inactive": "Inactive",
        "listening": "Listening for wake word...",
        "type_msg": "Type a message...",
        "conversation": "Conversation",
        "welcome_msg": "Hello, I am ATLAS.\nBackend is offline.\nSome features may be limited.\nHow can I assist you today?",
        "sys_stats": "System Stats",
        "cpu_usage": "CPU Usage",
        "ram_usage": "RAM Usage",
        "disk": "Disk",
        "weather": "Weather",
        "camera": "Camera",
        "camera_inactive": "Camera is inactive. Click the power button to start.",
        "sys_uptime": "System Uptime",
        "running_for": "System Running For:",
        "session": "Session",
        "commands": "Commands",
        "sys_load": "System Load",
        "moderate": "Moderate",
        "humidity": "Humidity",
        "wind": "Wind",
        "feels": "Feels Like",
        "city_not_set": "City not set",
        "config_title": "Configuration",
        "tab_clima": "Weather",
        "tab_api": "API + Model",
        "tab_general": "General",
        "clima_search": "Search city for weather:",
        "clima_example": "E.g.: medellin, london, queretaro, tokyo",
        "clima_search_btn": "Search",
        "clima_save_btn": "Save displayed city",
        "clima_preview": "Weather summary",
        "clima_city": "City:",
        "clima_temp": "Temperature:",
        "clima_desc": "Condition:",
        "clima_hum": "Humidity:",
        "clima_wind": "Wind:",
        "clima_feel": "Feels like:",
        "api_key_label": "Ollama Cloud API Key:",
        "api_key_hint": "Your Ollama Cloud API key to connect the assistant",
        "model_label": "AI Model:",
        "model_hint": "Model that ATLAS will use to respond",
        "temp_label": "Temperature (0.0 - 1.0):",
        "temp_hint": "Controls model creativity (higher = more creative)",
        "save_api_btn": "Save API + Model",
        "gen_label": "General settings",
        "gen_hint": "More general options will appear here in future updates.",
        "lang_label": "Idioma / Language:",
        "save_all_btn": "Save all",
        "close_btn": "Close",
        "searching": "Searching...",
        "no_results": "No cities found",
        "loading_weather": "Loading weather...",
        "weather_error": "Error fetching weather",
        "conn_error": "Connection error",
        "save_city_first": "First search and select a city.",
        "city_saved": "City saved:",
        "enter_city": "Enter a city name.",
        "api_empty_warn": "API Key cannot be empty.",
        "api_saved": "API Key, model and temperature saved.",
        "all_saved": "All settings saved.",
        "lang_saved": "Language changed to",
        "system_stats": "System Stats",
        "cpu_box": "CPU",
        "mem_box": "Memory",
    },
}


class Particle:
    def __init__(self, w, h):
        self.x = random.randint(0, w)
        self.y = random.randint(0, h)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.3, 0.3)
        self.r = random.uniform(0.8, 2)
        self.alpha = random.uniform(0.1, 0.4)


class AtlasAnim:
    def __init__(self, canvas, w, h):
        self.canvas = canvas
        self.w = w
        self.h = h
        self.cx = w // 2
        self.cy = h // 2
        self.angle = 0
        self.pulse = 0
        self.particles = [Particle(w, h) for _ in (30 if w < 400 else 50)]
        self.running = True

    def draw(self):
        self.canvas.delete("anim")
        cx, cy = self.cx, self.cy
        a = self.angle
        p = self.pulse

        for pt in self.particles:
            pt.x += pt.vx
            pt.y += pt.vy
            if pt.x < 0 or pt.x > self.w:
                pt.vx *= -1
            if pt.y < 0 or pt.y > self.h:
                pt.vy *= -1
            c = self._rgba(60, 160, 255, pt.alpha)
            self.canvas.create_oval(pt.x - pt.r, pt.y - pt.r, pt.x + pt.r, pt.y + pt.r, fill=c, outline="", tags="anim")

        rings = [30, 55, 85, 115, 150]
        for i, br in enumerate(rings):
            r = br + 8 * math.sin(p * 0.5 + i * 0.9)
            alpha = 0.15 + 0.2 * math.sin(p * 0.4 + i * 0.6) + 0.1
            c = self._rgba(0, 140 + i * 20, 220 + i * 5, min(alpha, 0.9))
            w = 1 if i < 2 else 2
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=c, width=w, tags="anim")

        sr = 170
        ex = cx + sr * math.cos(a)
        ey = cy + sr * math.sin(a)
        self.canvas.create_line(cx, cy, ex, ey, fill="#0077aa", width=1, tags="anim")

        self.canvas.create_arc(cx - 130, cy - 130, cx + 130, cy + 130,
            start=math.degrees(a) - 20, extent=40,
            outline="#00ccff", width=2, tags="anim", style="arc")

        for i in range(6):
            aa = a + i * math.pi / 3
            x1 = cx + 80 * math.cos(aa)
            y1 = cy + 80 * math.sin(aa)
            x2 = cx + 105 * math.cos(aa)
            y2 = cy + 105 * math.sin(aa)
            b = 100 + 155 * (0.5 + 0.5 * math.sin(p + i))
            c = self._rgba(0, b, 255, 0.6)
            self.canvas.create_line(x1, y1, x2, y2, fill=c, width=2, tags="anim")

        gr = 12 + 5 * math.sin(p * 1.3)
        for g in [gr + 6, gr]:
            al = 0.08 if g > gr + 2 else 0.2
            c = self._rgba(0, 100, 200, al)
            self.canvas.create_oval(cx - g, cy - g, cx + g, cy + g, fill=c, outline="", tags="anim")
        self.canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill="#00ccff", outline="", tags="anim")

        self.angle += 0.015
        self.pulse += 0.02
        if self.running:
            self.canvas.after(40, self.draw)

    def stop(self):
        self.running = False

    def _rgba(self, r, g, b, a):
        return f"#{max(0,min(255,int(r))):02x}{max(0,min(255,int(g))):02x}{max(0,min(255,int(b))):02x}"


def glass_frame(parent, **kwargs):
    kw = {"fg_color": PANEL_COLOR, "corner_radius": 12, "border_width": 1, "border_color": BORDER_COLOR}
    kw.update(kwargs)
    return ctk.CTkFrame(parent, **kw)


class MainWindow:
    def __init__(self):
        load_dotenv(ENV_PATH)
        self.lang_code = os.getenv("ATLAS_LANG", "es")
        if self.lang_code not in LANG:
            self.lang_code = "es"
        self.tr = LANG[self.lang_code]

        self.window = ctk.CTk()
        self.window.title(self.tr["window_title"])
        self.window.geometry("1400x800")
        self.window.minsize(1200, 680)

        self.sys_stats = {"cpu": 0, "ram_pct": 0, "ram_used": 0, "ram_total": 0, "disk_used": 0, "disk_total": 0}
        self.weather_data = None
        self.ollama = OllamaClient(api_key=os.getenv("OLLAMA_API_KEY", ""))
        self.ollama_models = []
        self.ollama_verified = False

        system_prompt = self._load_soul()
        self.messages = [{"role": "system", "content": system_prompt}]

        self._build()
        self._load_chat_history()
        self.window.after(500, self._auto_verify_ollama)

    def _auto_verify_ollama(self):
        key = os.getenv("OLLAMA_API_KEY", "")
        if key:
            self.ollama.set_api_key(key)
            def work():
                ok, msg = self.ollama.verify()
                if ok:
                    models = self.ollama.list_models(force=True) or []
                    self.ollama_models = models
                    self.ollama_verified = True
                    model_ids = [m["id"] for m in models] if models else []
                    self.window.after(0, lambda: self._on_verify_success(msg, model_ids))
            threading.Thread(target=work, daemon=True).start()

    def _load_soul(self):
        try:
            with open(SOUL_PATH, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return "Eres ATLAS, un asistente personal inteligente. Responde en español."

    def _load_memory(self):
        try:
            with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("messages", [])
        except Exception:
            return []

    def _save_memory(self):
        try:
            history = [m for m in self.messages if m["role"] != "system"]
            with open(MEMORY_PATH, "w", encoding="utf-8") as f:
                json.dump({"messages": history[-50:]}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _clear_memory(self):
        self.messages = [m for m in self.messages if m["role"] == "system"]
        self._save_memory()
        for w in self.chat_inner.winfo_children():
            w.destroy()
        self._add_chat_message("assistant", self._tr("welcome_msg"))

    def _load_chat_history(self):
        history = self._load_memory()
        if not history:
            self._add_chat_message("assistant", self._tr("welcome_msg"))
            return
        for m in history[-30:]:
            self._add_chat_message(m["role"], m["content"])
            self.messages.append(m)

    def _tr(self, key):
        if key in self.tr:
            return self.tr[key]
        return LANG.get(self.lang_code, LANG["es"]).get(key, key)

    def _reload_lang(self):
        self.tr = LANG[self.lang_code]

    def _rebuild_ui(self):
        for widget in self.window.winfo_children():
            widget.destroy()
        self.window.title(self._tr("window_title"))
        if hasattr(self, 'anim') and self.anim:
            self.anim.stop()
        self._build()

    def _build(self):
        self.window.grid_rowconfigure(0, weight=0, minsize=50)
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_rowconfigure(2, weight=0, minsize=62)
        self.window.grid_columnconfigure(0, weight=0, minsize=290)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_columnconfigure(2, weight=0, minsize=340)

        self._create_topbar()
        self._create_left_panels()
        self._create_center()
        self._create_right_panel()
        self._create_bottombar()

        self.canvas.after(100, self._start_anim)
        self._update_system_stats()
        self._fetch_weather()

    # ─── TOP BAR ─────────────────────────────────
    def _create_topbar(self):
        bar = ctk.CTkFrame(self.window, fg_color="#080b14", corner_radius=0, height=50)
        bar.grid(row=0, column=0, columnspan=3, sticky="ew")
        bar.grid_columnconfigure(2, weight=1)
        bar.grid_propagate(False)

        left = ctk.CTkFrame(bar, fg_color="transparent")
        left.grid(row=0, column=0, padx=(18, 0), pady=0, sticky="w")
        ctk.CTkLabel(left, text="A T L A S", font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(left, text="  ●", font=ctk.CTkFont(size=13), text_color="#00cc44").pack(side="left", padx=(8, 0))
        self.status_lbl = ctk.CTkLabel(left, text=self._tr("online"), font=ctk.CTkFont(size=FONT_SM), text_color="#44cc66")
        self.status_lbl.pack(side="left", padx=(4, 0))

        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.grid(row=0, column=3, padx=(0, 18), pady=0, sticky="e")

        self._update_clock(right)

        sep = ctk.CTkLabel(right, text="|", text_color="#334466", font=ctk.CTkFont(size=FONT_MD))
        sep.pack(side="left", padx=8)

        ctk.CTkLabel(right, text="📅", font=ctk.CTkFont(size=FONT_SM)).pack(side="left")
        self.date_lbl = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=FONT_SM), text_color=TEXT_DIM)
        self.date_lbl.pack(side="left", padx=(4, 12))
        self._update_date()

        ctk.CTkLabel(right, text="🌤", font=ctk.CTkFont(size=FONT_SM)).pack(side="left")
        self.weather_top_lbl = ctk.CTkLabel(right, text="--", font=ctk.CTkFont(size=FONT_SM), text_color=TEXT_DIM)
        self.weather_top_lbl.pack(side="left", padx=(3, 12))

        self.gear_btn = ctk.CTkButton(right, text="⚙ " + self._tr("config_title"),
            command=self.show_config_frame,
            fg_color="#0a1a33", hover_color="#0f2a55", text_color=TEXT_BRIGHT,
            corner_radius=8, width=110, height=30, font=ctk.CTkFont(size=FONT_SM))
        self.gear_btn.pack(side="left")

        self._clock_updater()

    def _update_clock(self, parent):
        now = datetime.now()
        if hasattr(self, 'clock_lbl'):
            self.clock_lbl.destroy()
        self.clock_lbl = ctk.CTkLabel(parent, text=f"🕐 {now.strftime('%I:%M:%S %p').lstrip('0')}",
            font=ctk.CTkFont(size=FONT_SM), text_color=TEXT_DIM)
        self.clock_lbl.pack(side="left")

    def _update_date(self):
        self.date_lbl.configure(text=datetime.now().strftime("%B %d, %Y"))

    def _clock_updater(self):
        now = datetime.now()
        if hasattr(self, 'clock_lbl'):
            self.clock_lbl.configure(text=f"🕐 {now.strftime('%I:%M:%S %p').lstrip('0')}")
        self.window.after(1000, self._clock_updater)

    # ─── SYSTEM STATS ────────────────────────────
    def _update_system_stats(self):
        try:
            self.sys_stats["cpu"] = psutil.cpu_percent(interval=0)
            mem = psutil.virtual_memory()
            self.sys_stats["ram_pct"] = mem.percent
            self.sys_stats["ram_used"] = mem.used // (1024**3)
            self.sys_stats["ram_total"] = mem.total // (1024**3)
            disk = psutil.disk_usage('/')
            self.sys_stats["disk_used"] = disk.used // (1024**3)
            self.sys_stats["disk_total"] = disk.total // (1024**3)
        except Exception:
            pass

        self._refresh_system_panel()
        self._refresh_uptime_panel()
        self.window.after(2000, self._update_system_stats)

    # ─── WEATHER ─────────────────────────────────
    def _fetch_weather(self):
        city = os.getenv("WEATHER_CITY", "").strip()
        if not city:
            self.weather_data = None
            self._refresh_weather_panel()
            self.weather_top_lbl.configure(text="--")
            return

        def fetch():
            try:
                url = f"https://wttr.in/{city}?format=j1&lang={self.lang_code}"
                resp = requests.get(url, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    curr = data["current_condition"][0]
                    self.weather_data = {
                        "temp": curr["temp_C"],
                        "desc": curr["weatherDesc"][0]["value"],
                        "humidity": curr["humidity"],
                        "wind": curr["windspeedKmph"],
                        "feels": curr["FeelsLikeC"],
                        "city": city,
                    }
                else:
                    self.weather_data = None
            except Exception:
                self.weather_data = None

            self.window.after(0, self._refresh_weather_panel)
            self.window.after(0, self._refresh_weather_top)

        threading.Thread(target=fetch, daemon=True).start()

    def _refresh_weather_top(self):
        if self.weather_data:
            self.weather_top_lbl.configure(
                text=f"{self.weather_data['temp']}°C {self.weather_data['city']}")
        else:
            self.weather_top_lbl.configure(text="--")

    # ─── LEFT PANELS ─────────────────────────────
    def _create_left_panels(self):
        container = ctk.CTkFrame(self.window, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=4)
        container.grid_rowconfigure((0, 1, 2, 3), weight=1, uniform="left")
        container.grid_columnconfigure(0, weight=1)

        self._create_panel_system(container, 0)
        self._create_panel_weather(container, 1)
        self._create_panel_camera(container, 2)
        self._create_panel_uptime(container, 3)

    # Panel System Stats
    def _create_panel_system(self, parent, row):
        p = glass_frame(parent)
        p.grid(row=row, column=0, sticky="nsew", padx=2, pady=2)
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(4, weight=1)

        hdr = ctk.CTkFrame(p, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=12, pady=(10, 0), sticky="ew")
        ctk.CTkLabel(hdr, text=self._tr("system_stats"), font=ctk.CTkFont(size=FONT_MD, weight="bold"),
            text_color=TEXT_BRIGHT).pack(side="left")
        self.sys_refresh_lbl = ctk.CTkLabel(hdr, text="↻", font=ctk.CTkFont(size=FONT_SM), text_color=TEXT_DIM)
        self.sys_refresh_lbl.pack(side="right")

        self.sys_labels = {}
        stats = [("cpu", self._tr("cpu_usage")), ("ram", self._tr("ram_usage"))]
        for i, (key, label) in enumerate(stats):
            rf = ctk.CTkFrame(p, fg_color="transparent")
            rf.grid(row=1 + i, column=0, padx=12, pady=(8, 0), sticky="ew")
            rf.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(rf, text=label, font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM).grid(row=0, column=0, sticky="w")
            val_lbl = ctk.CTkLabel(rf, text="--", font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_BRIGHT)
            val_lbl.grid(row=0, column=2, sticky="e")
            bar = ctk.CTkProgressBar(rf, height=5, fg_color="#0a1a2a", progress_color=ACCENT, corner_radius=2)
            bar.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(3, 0))
            bar.set(0)
            self.sys_labels[key] = (val_lbl, bar)

        boxes = ctk.CTkFrame(p, fg_color="transparent")
        boxes.grid(row=3, column=0, padx=12, pady=(10, 4), sticky="ew")
        boxes.grid_columnconfigure((0, 1), weight=1)
        self.sys_box_labels = {}
        for i, (k, label) in enumerate([("cpu_box", self._tr("cpu_box")), ("mem_box", self._tr("mem_box"))]):
            b = ctk.CTkFrame(boxes, fg_color="#0a1220", corner_radius=6)
            b.grid(row=0, column=i, sticky="ew", padx=2)
            ctk.CTkLabel(b, text=label, font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM).pack()
            val = ctk.CTkLabel(b, text="--", font=ctk.CTkFont(size=FONT_MD, weight="bold"), text_color=ACCENT)
            val.pack()
            self.sys_box_labels[k] = val

        self.disk_lbl = ctk.CTkLabel(p, text=self._tr("disk") + ": --", font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM)
        self.disk_lbl.grid(row=4, column=0, padx=12, pady=(4, 10), sticky="w")

    def _refresh_system_panel(self):
        s = self.sys_stats
        if "cpu" in self.sys_labels:
            vl, bar = self.sys_labels["cpu"]
            vl.configure(text=f"{s['cpu']}%")
            bar.set(s["cpu"] / 100)
        if "ram" in self.sys_labels:
            vl, bar = self.sys_labels["ram"]
            vl.configure(text=f"{s['ram_used']} GB / {s['ram_total']} GB")
            bar.set(s["ram_pct"] / 100)

        if "cpu_box" in self.sys_box_labels:
            self.sys_box_labels["cpu_box"].configure(text=f"{s['cpu']}%")
        if "mem_box" in self.sys_box_labels:
            self.sys_box_labels["mem_box"].configure(text=f"{s['ram_pct']}%")

        self.disk_lbl.configure(text=f"{self._tr('disk')}: {s['disk_used']} / {s['disk_total']} GB")

    # Panel Weather
    def _create_panel_weather(self, parent, row):
        p = glass_frame(parent)
        p.grid(row=row, column=0, sticky="nsew", padx=2, pady=2)
        p.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(p, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=12, pady=(8, 0), sticky="ew")
        ctk.CTkLabel(hdr, text=self._tr("weather"), font=ctk.CTkFont(size=FONT_MD, weight="bold"),
            text_color=TEXT_BRIGHT).pack(side="left")
        ctk.CTkLabel(hdr, text="↻", font=ctk.CTkFont(size=FONT_SM), text_color=TEXT_DIM).pack(side="right")

        body = ctk.CTkFrame(p, fg_color="transparent")
        body.grid(row=1, column=0, padx=12, pady=6, sticky="ew")
        body.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(body, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")
        self.weather_icon_lbl = ctk.CTkLabel(top, text="☁", font=ctk.CTkFont(size=32), text_color="#7799bb")
        self.weather_icon_lbl.pack(side="left", padx=(0, 10))
        self.weather_temp_lbl = ctk.CTkLabel(top, text="--", font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_BRIGHT)
        self.weather_temp_lbl.pack(side="left")
        self.weather_desc_lbl = ctk.CTkLabel(top, text="", font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM)
        self.weather_desc_lbl.pack(side="right")

        self.weather_city_lbl = ctk.CTkLabel(body, text=self._tr("city_not_set"), font=ctk.CTkFont(size=FONT_SM),
            text_color=TEXT_DIM)
        self.weather_city_lbl.grid(row=1, column=0, sticky="w", pady=(4, 0))

        mini = ctk.CTkFrame(body, fg_color="transparent")
        mini.grid(row=2, column=0, sticky="ew", pady=(6, 8))
        self.weather_hum_lbl = ctk.CTkLabel(mini, text=self._tr("humidity") + ": --", font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM)
        self.weather_hum_lbl.pack(side="left", padx=(0, 8))
        self.weather_wind_lbl = ctk.CTkLabel(mini, text=self._tr("wind") + ": --", font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM)
        self.weather_wind_lbl.pack(side="left", padx=(0, 8))
        self.weather_feel_lbl = ctk.CTkLabel(mini, text=self._tr("feels") + ": --", font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM)
        self.weather_feel_lbl.pack(side="left")

    def _refresh_weather_panel(self):
        w = self.weather_data
        if w:
            self.weather_temp_lbl.configure(text=f"{w['temp']}°C")
            self.weather_desc_lbl.configure(text=w["desc"])
            self.weather_city_lbl.configure(text=w["city"])
            self.weather_hum_lbl.configure(text=f"{self._tr('humidity')}: {w['humidity']}%")
            self.weather_wind_lbl.configure(text=f"{self._tr('wind')}: {w['wind']} m/s")
            self.weather_feel_lbl.configure(text=f"{self._tr('feels')}: {w['feels']}°C")
        else:
            self.weather_temp_lbl.configure(text="--")
            self.weather_desc_lbl.configure(text="")
            self.weather_city_lbl.configure(text=self._tr("city_not_set"))
            self.weather_hum_lbl.configure(text=self._tr("humidity") + ": --")
            self.weather_wind_lbl.configure(text=self._tr("wind") + ": --")
            self.weather_feel_lbl.configure(text=self._tr("feels") + ": --")

    # Panel Camera
    def _create_panel_camera(self, parent, row):
        p = glass_frame(parent)
        p.grid(row=row, column=0, sticky="nsew", padx=2, pady=2)
        p.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(p, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=12, pady=(8, 0), sticky="ew")
        ctk.CTkLabel(hdr, text=self._tr("camera"), font=ctk.CTkFont(size=FONT_MD, weight="bold"),
            text_color=TEXT_BRIGHT).pack(side="left")
        ctk.CTkLabel(hdr, text="📷  🖼  ⏻", font=ctk.CTkFont(size=FONT_SM), text_color=TEXT_DIM).pack(side="right")

        cam_box = ctk.CTkFrame(p, fg_color="#040810", corner_radius=8, height=60)
        cam_box.grid(row=1, column=0, padx=12, pady=(10, 0), sticky="ew")
        cam_box.grid_propagate(False)
        ctk.CTkLabel(cam_box, text="📷", font=ctk.CTkFont(size=24), text_color="#334455").pack(expand=True)
        ctk.CTkLabel(p, text=self._tr("camera_inactive"),
            font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM).grid(row=2, column=0, padx=12, pady=(6, 10))

    # Panel System Uptime
    def _create_panel_uptime(self, parent, row):
        p = glass_frame(parent)
        p.grid(row=row, column=0, sticky="nsew", padx=2, pady=2)
        p.grid_columnconfigure(0, weight=1)
        self.uptime_panel = p

        hdr = ctk.CTkFrame(p, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=12, pady=(8, 0), sticky="ew")
        ctk.CTkLabel(hdr, text=self._tr("sys_uptime"), font=ctk.CTkFont(size=FONT_MD, weight="bold"),
            text_color=TEXT_BRIGHT).pack(side="left")
        self.uptime_header_lbl = ctk.CTkLabel(hdr, text="--", font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM)
        self.uptime_header_lbl.pack(side="right")

        ctk.CTkLabel(p, text=self._tr("running_for"), font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM).grid(
            row=1, column=0, padx=12, pady=(6, 0), sticky="w")
        self.uptime_val_lbl = ctk.CTkLabel(p, text="--", font=ctk.CTkFont(size=22, weight="bold"),
            text_color=ACCENT)
        self.uptime_val_lbl.grid(row=2, column=0, padx=12, sticky="w")

        boxes = ctk.CTkFrame(p, fg_color="transparent")
        boxes.grid(row=3, column=0, padx=12, pady=(6, 2), sticky="ew")
        boxes.grid_columnconfigure((0, 1), weight=1)
        self.uptime_box_labels = {}
        for i, (k, label) in enumerate([("session", self._tr("session")), ("commands", self._tr("commands"))]):
            b = ctk.CTkFrame(boxes, fg_color="#0a1220", corner_radius=6)
            b.grid(row=0, column=i, sticky="ew", padx=2)
            ctk.CTkLabel(b, text=label, font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM).pack()
            val = ctk.CTkLabel(b, text="--", font=ctk.CTkFont(size=FONT_MD, weight="bold"), text_color=ACCENT)
            val.pack()
            self.uptime_box_labels[k] = val

        load_f = ctk.CTkFrame(p, fg_color="transparent")
        load_f.grid(row=4, column=0, padx=12, pady=(4, 10), sticky="ew")
        load_f.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(load_f, text=self._tr("sys_load") + ":", font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM).grid(row=0, column=0, sticky="w")
        self.load_pct_lbl = ctk.CTkLabel(load_f, text="--", font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM)
        self.load_pct_lbl.grid(row=0, column=2, sticky="e")
        self.load_bar = ctk.CTkProgressBar(load_f, height=5, fg_color="#0a1a2a", progress_color="#ffaa00", corner_radius=2)
        self.load_bar.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(3, 0))

    def _refresh_uptime_panel(self):
        try:
            uptime_sec = psutil.boot_time()
            delta = datetime.now() - datetime.fromtimestamp(uptime_sec)
            total_sec = int(delta.total_seconds())
            h, r = divmod(total_sec, 3600)
            m, s = divmod(r, 60)
            uptime_str = f"{h:02d}:{m:02d}:{s:02d}"
            self.uptime_val_lbl.configure(text=uptime_str)
            self.uptime_header_lbl.configure(text=uptime_str)

            load = psutil.getloadavg()
            load_pct = min(100, int((load[0] / psutil.cpu_count()) * 100))
            self.load_pct_lbl.configure(text=f"{self._tr('moderate')} {load_pct}%")
            self.load_bar.set(load_pct / 100)

            if "session" in self.uptime_box_labels:
                self.uptime_box_labels["session"].configure(text="1")
            if "commands" in self.uptime_box_labels:
                self.uptime_box_labels["commands"].configure(text="0")
        except Exception:
            pass

    # ─── CENTER ──────────────────────────────────
    def _create_center(self):
        center = ctk.CTkFrame(self.window, fg_color="#04070d", corner_radius=0)
        center.grid(row=1, column=1, sticky="nsew", padx=2, pady=4)
        center.grid_columnconfigure(0, weight=1)
        center.grid_rowconfigure(0, weight=1)

        self.canvas = Canvas(center, bg="#04070d", highlightthickness=0, borderwidth=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", self._on_resize)

        overlay = ctk.CTkFrame(center, fg_color="transparent")
        overlay.place(relx=0.5, rely=0.5, anchor="center")

        self.title_lbl = ctk.CTkLabel(overlay, text="A T L A S",
            font=ctk.CTkFont(size=30, weight="bold"), text_color=ACCENT)
        self.title_lbl.pack()

        status_f = ctk.CTkFrame(overlay, fg_color="transparent")
        status_f.pack(pady=(6, 0))
        ctk.CTkLabel(status_f, text="●", font=ctk.CTkFont(size=11), text_color="#00cc44").pack(side="left", padx=(0, 5))
        ctk.CTkLabel(status_f, text=self._tr("listening"),
            font=ctk.CTkFont(size=FONT_SM), text_color=TEXT_DIM).pack(side="left")

        tab = ctk.CTkLabel(center, text="◀", font=ctk.CTkFont(size=11),
            fg_color="#2a1a44", text_color="#9966ff", corner_radius=4, width=16, height=34)
        tab.place(relx=0, rely=0.5, anchor="w")

    def _on_resize(self, e):
        if hasattr(self, 'anim') and self.anim:
            self.anim.w = e.width
            self.anim.h = e.height
            self.anim.cx = e.width // 2
            self.anim.cy = e.height // 2

    def _start_anim(self):
        w = self.canvas.winfo_width() or 500
        h = self.canvas.winfo_height() or 500
        self.anim = AtlasAnim(self.canvas, w, h)
        self.anim.draw()

    # ─── RIGHT PANEL ─────────────────────────────
    def _create_right_panel(self):
        p = glass_frame(self.window)
        p.grid(row=1, column=2, sticky="nsew", padx=(4, 8), pady=4)
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(2, weight=1)

        hdr = ctk.CTkFrame(p, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="ew")
        ctk.CTkLabel(hdr, text=self._tr("conversation"), font=ctk.CTkFont(size=FONT_MD, weight="bold"),
            text_color=TEXT_BRIGHT).pack(side="left")
        clear_btn = ctk.CTkButton(hdr, text="🗑",
            command=self._clear_memory,
            fg_color="transparent", hover_color="#331122", text_color=TEXT_DIM,
            width=28, height=28, corner_radius=4, font=ctk.CTkFont(size=FONT_SM))
        clear_btn.pack(side="right", padx=(4, 0))
        ctk.CTkLabel(hdr, text="⬇", font=ctk.CTkFont(size=FONT_SM), text_color=TEXT_DIM).pack(side="right")

        self.chat_area = ctk.CTkFrame(p, fg_color="#060a14", corner_radius=8)
        self.chat_area.grid(row=2, column=0, padx=12, pady=4, sticky="nsew")
        self.chat_area.grid_columnconfigure(0, weight=1)
        self.chat_area.grid_rowconfigure(0, weight=1)

        self.chat_canvas = Canvas(self.chat_area, bg="#060a14", highlightthickness=0, borderwidth=0)
        self.chat_canvas.grid(row=0, column=0, sticky="nsew")
        self.chat_canvas.grid_rowconfigure(0, weight=1)

        self.chat_inner = ctk.CTkFrame(self.chat_canvas, fg_color="transparent")
        self.chat_canvas.create_window((0, 0), window=self.chat_inner, anchor="nw", tags="inner")

        self.chat_scroll = ctk.CTkScrollbar(self.chat_area, orientation="vertical", command=self.chat_canvas.yview)
        self.chat_scroll.grid(row=0, column=1, sticky="ns")
        self.chat_canvas.configure(yscrollcommand=self.chat_scroll.set)

        self.chat_inner.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        self.chat_canvas.bind("<Configure>", self._on_chat_resize)

        self._add_chat_message("assistant", self._tr("welcome_msg"))

        self.chat_time_lbl = ctk.CTkLabel(p, text=datetime.now().strftime("%I:%M %p").lstrip('0'),
            font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM)
        self.chat_time_lbl.grid(row=3, column=0, padx=18, pady=(4, 8), sticky="w")

    def _on_chat_resize(self, e):
        self.chat_canvas.itemconfig("inner", width=e.width)

    def _add_chat_message(self, role, text):
        bubble = ctk.CTkFrame(self.chat_inner, fg_color="#0c1428" if role == "assistant" else "#0a2233",
            corner_radius=8)
        bubble.pack(fill="x", padx=6, pady=4)
        ctk.CTkLabel(bubble, text=text, font=ctk.CTkFont(size=FONT_SM),
            text_color=TEXT_BRIGHT, justify="left", wraplength=260).pack(padx=10, pady=8, anchor="w")
        self.chat_inner.update_idletasks()
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.chat_canvas.yview_moveto(1.0)

    # ─── BOTTOM BAR ──────────────────────────────
    def _create_bottombar(self):
        bar = ctk.CTkFrame(self.window, fg_color="#080b14", corner_radius=0, height=62)
        bar.grid(row=2, column=0, columnspan=3, sticky="ew")
        bar.grid_propagate(False)

        content = ctk.CTkFrame(bar, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        for icon in ["🎥", "🎤", "⌨️"]:
            lbl = ctk.CTkLabel(content, text=icon, font=ctk.CTkFont(size=18), text_color=TEXT_DIM)
            lbl.pack(side="left", padx=6)

        self.chat_entry = ctk.CTkEntry(content, width=420, height=36,
            fg_color="#0a1220", border_color="#1a2a44", text_color=TEXT_BRIGHT,
            placeholder_text=self._tr("type_msg"), font=ctk.CTkFont(size=FONT_SM))
        self.chat_entry.pack(side="left", padx=(12, 8))
        self.chat_entry.bind("<Return>", self._send_message)

        send_btn = ctk.CTkButton(content, text="📤", command=self._send_message,
            fg_color="#004466", hover_color="#006688", width=40, height=36,
            corner_radius=8, font=ctk.CTkFont(size=16))
        send_btn.pack(side="left")

    def _send_message(self, e=None):
        msg = self.chat_entry.get().strip()
        if not msg:
            return
        self._add_chat_message("user", msg)
        self.chat_entry.delete(0, "end")
        self.chat_time_lbl.configure(text=datetime.now().strftime("%I:%M %p").lstrip('0'))
        self._ask_ollama(msg)

    def _ask_ollama(self, msg):
        if not self.ollama_verified:
            txt = ("⚠️ No hay conexión con Ollama. Ve a Configuración → API + Modelo y verifica tu API key."
                   if self.lang_code == "es"
                   else "⚠️ No connection to Ollama. Go to Settings → API + Model and verify your API key.")
            self._add_chat_message("assistant", txt)
            return

        handled, result = process_message(msg)
        if handled:
            self._add_chat_message("assistant", f"✅ {result}")
            self.messages.append({"role": "user", "content": msg})
            self.messages.append({"role": "assistant", "content": f"✅ {result}"})
            self._save_memory()
            return

        thinking_frame = ctk.CTkFrame(self.chat_inner, fg_color="#0c1428", corner_radius=8)
        thinking_frame.pack(fill="x", padx=6, pady=4)
        thinking_lbl = ctk.CTkLabel(thinking_frame, text="⏳ ...", font=ctk.CTkFont(size=FONT_SM),
            text_color=TEXT_DIM, justify="left", wraplength=260)
        thinking_lbl.pack(padx=10, pady=8, anchor="w")
        self.chat_canvas.yview_moveto(1.0)

        def update_thinking(text):
            self.window.after(0, lambda: thinking_lbl.configure(text=text))

        def work():
            model = os.getenv("OLLAMA_MODEL", "llama3")
            temp = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))

            update_thinking("🌐 Buscando en internet...")
            tavily_key = os.getenv("TAVILY_API_KEY", "")
            web_info = search_web(msg, tavily_api_key=tavily_key or None)

            update_thinking("⏳ Pensando...")
            full = list(self.messages)
            today = datetime.now().strftime("%d/%m/%Y")
            if web_info:
                trimmed = "\n".join(web_info.split("\n")[:80])
                user_msg_combined = (
                    f"[Contexto — {today}]\n{trimmed}\n\n"
                    f"---\n{msg}\n\n"
                    f"Importante: lista TODOS los elementos disponibles, no hagas resúmenes."
                )
            else:
                user_msg_combined = f"[Contexto — {today}]\n\n{msg}"
            full.append({"role": "user", "content": user_msg_combined})
            ok, result = self.ollama.chat(model, full, temperature=temp)
            self.window.after(0, lambda: self._handle_chat_response(thinking_frame, ok, result, msg))

        threading.Thread(target=work, daemon=True).start()

    def _handle_chat_response(self, thinking_frame, ok, result, user_msg):
        thinking_frame.destroy()
        if ok:
            self.messages.append({"role": "user", "content": user_msg})
            self.messages.append({"role": "assistant", "content": result})
            self._add_chat_message("assistant", result)
            self._save_memory()
        else:
            self._add_chat_message("assistant", "❌ " + result)

    # ─── CONFIG OVERLAY ──────────────────────────
    def _make_overlay(self):
        self._close_overlay()
        self.overlay = ctk.CTkFrame(self.window, fg_color="#060a14", corner_radius=0)
        self.overlay.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=80, pady=40)
        self.overlay.grid_columnconfigure(0, weight=1)
        self.overlay.grid_rowconfigure(1, weight=1)
        return self.overlay

    def _close_overlay(self, e=None):
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.destroy()
            self.overlay = None

    def show_config_frame(self):
        parent = self._make_overlay()

        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.grid(row=0, column=0, padx=30, pady=(20, 10), sticky="ew")
        ctk.CTkLabel(top, text="⚙ " + self._tr("config_title"),
            font=ctk.CTkFont(size=24, weight="bold"), text_color=ACCENT).pack(side="left")
        ctk.CTkButton(top, text="✕ " + self._tr("close_btn"),
            command=self._close_overlay,
            fg_color="#331122", hover_color="#553344", text_color="#cc6677",
            width=90, height=32, corner_radius=6, font=ctk.CTkFont(size=FONT_SM)
        ).pack(side="right")

        tabview = ctk.CTkTabview(parent,
            fg_color="#080c18", segmented_button_fg_color="#0a1220",
            segmented_button_selected_color="#004466",
            segmented_button_selected_hover_color="#006688",
            segmented_button_unselected_color="#0a1220",
            segmented_button_unselected_hover_color="#112244",
            text_color=TEXT_BRIGHT, corner_radius=10, height=420)
        tabview.grid(row=1, column=0, padx=30, pady=10, sticky="nsew")

        # ── Tab: Clima ──
        t_clima = tabview.add("🌤  " + self._tr("tab_clima"))
        t_clima.grid_columnconfigure(0, weight=1)
        t_clima.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(t_clima, text=self._tr("clima_search"),
            font=ctk.CTkFont(size=FONT_MD, weight="bold"), text_color=TEXT_BRIGHT
        ).grid(row=0, column=0, padx=20, pady=(25, 8), sticky="w")

        search_f = ctk.CTkFrame(t_clima, fg_color="transparent")
        search_f.grid(row=1, column=0, padx=20, pady=4, sticky="w")
        self.city_entry = ctk.CTkEntry(search_f, width=300, height=36,
            font=ctk.CTkFont(size=FONT_SM), fg_color="#0a1220", border_color="#1a2a44")
        self.city_entry.pack(side="left")
        ctk.CTkButton(search_f, text="🔍 " + self._tr("clima_search_btn"),
            command=self._search_cities,
            fg_color="#004466", hover_color="#006688", corner_radius=8, height=34, width=90,
            font=ctk.CTkFont(size=FONT_SM)
        ).pack(side="left", padx=(8, 0))
        ctk.CTkLabel(t_clima, text=self._tr("clima_example"),
            font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM
        ).grid(row=2, column=0, padx=20, pady=(0, 6), sticky="w")

        self.search_results = ctk.CTkScrollableFrame(t_clima, fg_color="#060a14",
            corner_radius=8, height=120)
        self.search_results.grid(row=3, column=0, padx=20, pady=4, sticky="ew")

        self.weather_preview = ctk.CTkFrame(t_clima, fg_color="#060a14", corner_radius=10,
            border_width=1, border_color="#1a2a44")
        self.weather_preview.grid(row=5, column=0, padx=20, pady=(6, 16), sticky="ew")
        self.weather_preview.grid_columnconfigure(0, weight=1)

        preview_inner = ctk.CTkFrame(self.weather_preview, fg_color="transparent")
        preview_inner.grid(row=0, column=0, padx=16, pady=10, sticky="ew")
        preview_inner.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(preview_inner, text=self._tr("clima_preview"),
            font=ctk.CTkFont(size=FONT_SM, weight="bold"), text_color=TEXT_BRIGHT
        ).grid(row=0, column=0, columnspan=3, pady=(0, 8), sticky="w")

        self.pv_icon = ctk.CTkLabel(preview_inner, text="☁", font=ctk.CTkFont(size=26), text_color="#7799bb")
        self.pv_icon.grid(row=1, column=0, rowspan=4, padx=(0, 14), sticky="ns")

        labels = [
            ("clima_city", "pv_city", "--"),
            ("clima_temp", "pv_temp", "--"),
            ("clima_desc", "pv_desc", "--"),
            ("clima_hum", "pv_hum", "--"),
            ("clima_wind", "pv_wind", "--"),
            ("clima_feel", "pv_feel", "--"),
        ]
        self.pv_labels = {}
        for i, (lbl_key, key, default) in enumerate(labels):
            ctk.CTkLabel(preview_inner, text=self._tr(lbl_key), font=ctk.CTkFont(size=FONT_XS),
                text_color=TEXT_DIM).grid(row=1+i, column=1, sticky="w")
            lbl2 = ctk.CTkLabel(preview_inner, text=default, font=ctk.CTkFont(size=FONT_XS),
                text_color=TEXT_BRIGHT)
            lbl2.grid(row=1+i, column=2, padx=(10, 0), sticky="w")
            self.pv_labels[key] = lbl2

        ctk.CTkButton(t_clima, text="💾 " + self._tr("clima_save_btn"),
            command=self._save_weather_only,
            fg_color="#0a1a33", hover_color="#112244", corner_radius=8, height=34,
            font=ctk.CTkFont(size=FONT_SM)
        ).grid(row=6, column=0, padx=20, pady=(0, 16), sticky="w")

        # ── Tab: API + Modelo ──
        t_api = tabview.add("🔑🤖  " + self._tr("tab_api"))
        t_api.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(t_api, text=self._tr("api_key_label"),
            font=ctk.CTkFont(size=FONT_MD, weight="bold"), text_color=TEXT_BRIGHT
        ).grid(row=0, column=0, padx=20, pady=(25, 8), sticky="w")
        self.api_key_entry = ctk.CTkEntry(t_api, width=480, show="*", height=36,
            font=ctk.CTkFont(size=FONT_SM), fg_color="#0a1220", border_color="#1a2a44")
        self.api_key_entry.grid(row=1, column=0, padx=20, pady=(0, 4), sticky="w")
        saved_key = os.getenv("OLLAMA_API_KEY", "")
        if saved_key:
            self.api_key_entry.insert(0, saved_key)
        ctk.CTkLabel(t_api, text=self._tr("api_key_hint"),
            font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM
        ).grid(row=2, column=0, padx=20, pady=(0, 8), sticky="w")

        # verify button + status
        verify_f = ctk.CTkFrame(t_api, fg_color="transparent")
        verify_f.grid(row=3, column=0, padx=20, pady=4, sticky="w")
        ctk.CTkButton(verify_f, text="🔍 " + ("Verificar API y cargar modelos" if self.lang_code == "es"
            else "Verify API & load models"),
            command=self._verify_ollama,
            fg_color="#004466", hover_color="#006688", corner_radius=8, height=34,
            font=ctk.CTkFont(size=FONT_SM)
        ).pack(side="left")
        self.api_status_lbl = ctk.CTkLabel(verify_f, text="", font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM)
        self.api_status_lbl.pack(side="left", padx=(12, 0))

        # Tavily Search API
        tavily_row = 4
        ctk.CTkLabel(t_api, text="Tavily API Key (recomendada):",
            font=ctk.CTkFont(size=FONT_MD, weight="bold"), text_color=TEXT_BRIGHT
        ).grid(row=tavily_row, column=0, padx=20, pady=(10, 8), sticky="w")
        self.tavily_key_entry = ctk.CTkEntry(t_api, width=480, show="*", height=36,
            font=ctk.CTkFont(size=FONT_SM), fg_color="#0a1220", border_color="#1a2a44")
        self.tavily_key_entry.grid(row=tavily_row + 1, column=0, padx=20, pady=(0, 4), sticky="w")
        saved_tavily = os.getenv("TAVILY_API_KEY", "")
        if saved_tavily:
            self.tavily_key_entry.insert(0, saved_tavily)
        ctk.CTkLabel(t_api, text=("API key de Tavily (tavily.com). "
                                  "Busca en internet y extrae el contenido completo de las páginas. "
                                  "Deja vacío para usar DuckDuckGo."
                                  if self.lang_code == "es"
                                  else "Tavily API key (tavily.com). "
                                  "Searches the web and extracts full page content. "
                                  "Leave empty for DuckDuckGo."),
            font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM
        ).grid(row=tavily_row + 2, column=0, padx=20, pady=(0, 8), sticky="w")

        sep = ctk.CTkFrame(t_api, height=1, fg_color="#1a2a44")
        sep.grid(row=tavily_row + 3, column=0, padx=20, sticky="ew", pady=8)

        br = tavily_row + 4
        ctk.CTkLabel(t_api, text=self._tr("model_label"),
            font=ctk.CTkFont(size=FONT_MD, weight="bold"), text_color=TEXT_BRIGHT
        ).grid(row=br, column=0, padx=20, pady=(10, 8), sticky="w")
        self.model_var = ctk.StringVar(value=os.getenv("OLLAMA_MODEL", "llama3"))
        self.model_menu = ctk.CTkOptionMenu(t_api,
            values=["llama3"],
            variable=self.model_var, fg_color="#0a1a33", button_color="#004466",
            font=ctk.CTkFont(size=FONT_SM), dropdown_font=ctk.CTkFont(size=FONT_SM), width=300)
        self.model_menu.grid(row=br + 1, column=0, padx=20, pady=(0, 4), sticky="w")
        ctk.CTkLabel(t_api, text=self._tr("model_hint"),
            font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM
        ).grid(row=br + 2, column=0, padx=20, pady=(0, 6), sticky="w")

        self.model_caps_lbl = ctk.CTkLabel(t_api, text="",
            font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM)
        self.model_caps_lbl.grid(row=br + 3, column=0, padx=20, pady=(0, 8), sticky="w")
        self.model_menu.configure(command=self._on_model_selected)
        self.window.after(200, self._on_model_selected)

        sep2 = ctk.CTkFrame(t_api, height=1, fg_color="#1a2a44")
        sep2.grid(row=br + 4, column=0, padx=20, sticky="ew", pady=4)

        ctk.CTkLabel(t_api, text=self._tr("temp_label"),
            font=ctk.CTkFont(size=FONT_MD, weight="bold"), text_color=TEXT_BRIGHT
        ).grid(row=br + 5, column=0, padx=20, pady=(10, 8), sticky="w")
        tf = ctk.CTkFrame(t_api, fg_color="transparent")
        tf.grid(row=br + 6, column=0, padx=20, pady=5, sticky="w")
        self.temp_slider = ctk.CTkSlider(tf, from_=0, to=1, number_of_steps=20,
            width=280, height=18,
            fg_color="#112244", progress_color=ACCENT, button_color="#0088cc",
            button_hover_color="#00aaee")
        self.temp_slider.pack(side="left")
        self.temp_slider.set(float(os.getenv("OLLAMA_TEMPERATURE", "0.7")))
        self.temp_label = ctk.CTkLabel(tf, text=f"{self.temp_slider.get():.1f}",
            font=ctk.CTkFont(size=FONT_MD))
        self.temp_label.pack(side="left", padx=(12, 0))
        self.temp_slider.configure(command=lambda v: self.temp_label.configure(text=f"{v:.1f}"))
        ctk.CTkLabel(t_api, text=self._tr("temp_hint"),
            font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM
        ).grid(row=br + 7, column=0, padx=20, pady=(2, 15), sticky="w")

        ctk.CTkButton(t_api, text="💾 " + self._tr("save_api_btn"),
            command=lambda: self._save_single("api_model"),
            fg_color="#004466", hover_color="#006688", corner_radius=8, height=34,
            font=ctk.CTkFont(size=FONT_SM)
        ).grid(row=br + 8, column=0, padx=20, pady=(10, 20), sticky="w")

        # ── Tab: General ──
        t_gen = tabview.add("⚙  " + self._tr("tab_general"))
        t_gen.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(t_gen, text=self._tr("gen_label"),
            font=ctk.CTkFont(size=FONT_MD, weight="bold"), text_color=TEXT_BRIGHT
        ).grid(row=0, column=0, padx=20, pady=(25, 8), sticky="w")
        ctk.CTkLabel(t_gen, text=self._tr("gen_hint"),
            font=ctk.CTkFont(size=FONT_SM), text_color=TEXT_DIM, justify="left"
        ).grid(row=1, column=0, padx=20, pady=10, sticky="w")

        ctk.CTkLabel(t_gen, text=self._tr("lang_label"),
            font=ctk.CTkFont(size=FONT_MD, weight="bold"), text_color=TEXT_BRIGHT
        ).grid(row=2, column=0, padx=20, pady=(15, 8), sticky="w")
        self.lang_var = ctk.StringVar(value=self.lang_code)
        lang_menu = ctk.CTkOptionMenu(t_gen,
            values=["es - Español", "en - English"],
            command=self._change_lang,
            fg_color="#0a1a33", button_color="#004466",
            font=ctk.CTkFont(size=FONT_SM), dropdown_font=ctk.CTkFont(size=FONT_SM), width=200)
        lang_menu.grid(row=3, column=0, padx=20, pady=(0, 4), sticky="w")
        lang_menu.set("es - Español" if self.lang_code == "es" else "en - English")

        ctk.CTkButton(t_gen, text="💾 " + self._tr("save_all_btn"),
            command=self._save_config_all,
            fg_color="#004466", hover_color="#006688", corner_radius=8, height=38,
            font=ctk.CTkFont(size=FONT_SM)
        ).grid(row=4, column=0, padx=20, pady=(25, 20), sticky="w")

    # ─── LANGUAGE ────────────────────────────────
    def _change_lang(self, choice):
        if choice.startswith("es"):
            self.lang_code = "es"
        else:
            self.lang_code = "en"
        set_key(ENV_PATH, "ATLAS_LANG", self.lang_code)
        self._reload_lang()
        messagebox.showinfo(self._tr("config_title"),
            f"{self._tr('lang_saved')}: {self.lang_code.upper()}")
        self._close_overlay()
        self._rebuild_ui()
        self._fetch_weather()

    # ─── OLLAMA VERIFY ────────────────────────────
    def _verify_ollama(self):
        key = self.api_key_entry.get().strip()
        if not key:
            messagebox.showwarning("Advertencia" if self.lang_code == "es" else "Warning",
                self._tr("api_empty_warn"))
            return
        self.ollama.set_api_key(key)
        self.api_status_lbl.configure(text="Verificando..." if self.lang_code == "es" else "Verifying...")

        def work():
            ok, msg = self.ollama.verify()
            if ok:
                models = self.ollama.list_models(force=True) or []
                self.ollama_models = models
                self.ollama_verified = True
                model_ids = [m["id"] for m in models] if models else []
                self.window.after(0, lambda: self._on_verify_success(msg, model_ids))
            else:
                self.window.after(0, lambda: self._on_verify_fail(msg))

        threading.Thread(target=work, daemon=True).start()

    def _on_verify_success(self, msg, model_ids):
        self.api_status_lbl.configure(text="✅ " + msg, text_color="#44cc66")
        if model_ids:
            self.model_menu.configure(values=model_ids)
            if self.model_var.get() not in model_ids:
                self.model_var.set(model_ids[0])
            self._on_model_selected()
        else:
            self.model_caps_lbl.configure(text="")

    def _on_verify_fail(self, msg):
        self.api_status_lbl.configure(text="❌ " + msg, text_color="#cc6677")
        self.ollama_verified = False
        self.model_caps_lbl.configure(text="")

    def _on_model_selected(self, choice=None):
        mid = self.model_var.get()
        if self.ollama_verified and self.ollama_models:
            info = self.ollama.get_model_info(mid)
            caps = []
            if info.get("has_vision"):
                caps.append("🖼️ " + ("Visión" if self.lang_code == "es" else "Vision"))
            if info.get("has_audio"):
                caps.append("🎤 " + ("Audio" if self.lang_code == "es" else "Audio"))
            if caps:
                self.model_caps_lbl.configure(
                    text="Capacidades: " + " | ".join(caps),
                    text_color="#00ccaa")
            else:
                self.model_caps_lbl.configure(
                    text="📝 " + ("Solo texto" if self.lang_code == "es" else "Text only"),
                    text_color=TEXT_DIM)
        else:
            self.model_caps_lbl.configure(text="")

    # ─── WEATHER SEARCH ──────────────────────────
    def _search_cities(self):
        query = self.city_entry.get().strip()
        if not query:
            messagebox.showwarning("Advertencia" if self.lang_code == "es" else "Warning",
                self._tr("enter_city"))
            return

        for w in self.search_results.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.search_results, text=self._tr("searching"),
            font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM).pack(pady=6)

        def search():
            try:
                url = "https://nominatim.openstreetmap.org/search"
                params = {"q": query, "format": "json", "limit": 6, "featuretype": "city"}
                headers = {"User-Agent": "ATLAS-Assistant/1.0"}
                resp = requests.get(url, params=params, headers=headers, timeout=8)
                results = resp.json() if resp.status_code == 200 else []
            except Exception:
                results = []
            self.window.after(0, lambda: self._show_city_results(results))

        threading.Thread(target=search, daemon=True).start()

    def _show_city_results(self, results):
        for w in self.search_results.winfo_children():
            w.destroy()

        if not results:
            ctk.CTkLabel(self.search_results, text=self._tr("no_results"),
                font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM).pack(pady=8)
            return

        for r in results:
            display_name = r.get("display_name", "")
            lat, lon = r.get("lat", ""), r.get("lon", "")
            name_parts = display_name.split(",")
            city = name_parts[0].strip() if name_parts else display_name
            extra = name_parts[1].strip() if len(name_parts) > 1 else ""
            country = name_parts[-1].strip() if len(name_parts) > 1 else ""
            short = f"{city}, {extra} — {country}" if extra else display_name

            btn = ctk.CTkButton(self.search_results, text=short,
                fg_color="transparent", hover_color="#0a1a33",
                text_color=TEXT_BRIGHT, anchor="w", height=28,
                font=ctk.CTkFont(size=FONT_XS), corner_radius=4)
            btn.pack(fill="x", padx=4, pady=1)
            btn.bind("<Button-1>", lambda e, n=display_name, lt=lat, ln=lon: self._select_city(n, lt, ln))

    def _select_city(self, name, lat, lon):
        self.city_entry.delete(0, "end")
        self.city_entry.insert(0, name)

        for w in self.search_results.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.search_results, text=self._tr("loading_weather"),
            font=ctk.CTkFont(size=FONT_XS), text_color=TEXT_DIM).pack(pady=6)

        def fetch():
            try:
                wurl = f"https://wttr.in/{lat},{lon}?format=j1&lang={self.lang_code}"
                resp = requests.get(wurl, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    curr = data["current_condition"][0]
                    area = data.get("nearest_area", [{}])[0]
                    resolved = area.get("areaName", [{}])[0].get("value", "")
                    region = area.get("region", [{}])[0].get("value", "")
                    country = area.get("country", [{}])[0].get("value", "")
                    full_city = f"{resolved}, {region}, {country}" if region else resolved
                    info = {
                        "city": full_city,
                        "temp": curr["temp_C"],
                        "desc": curr["weatherDesc"][0]["value"],
                        "humidity": curr["humidity"],
                        "wind": curr["windspeedKmph"],
                        "feels": curr["FeelsLikeC"],
                    }
                    self.window.after(0, lambda: self._update_preview(info))
                else:
                    self.window.after(0, lambda: self.pv_labels["pv_city"].configure(text=self._tr("weather_error")))
            except Exception:
                self.window.after(0, lambda: self.pv_labels["pv_city"].configure(text=self._tr("conn_error")))

        threading.Thread(target=fetch, daemon=True).start()

    def _update_preview(self, info):
        self.pv_labels["pv_city"].configure(text=info["city"])
        self.pv_labels["pv_temp"].configure(text=f"{info['temp']}°C")
        self.pv_labels["pv_desc"].configure(text=info["desc"])
        self.pv_labels["pv_hum"].configure(text=f"{info['humidity']}%")
        self.pv_labels["pv_wind"].configure(text=f"{info['wind']} km/h")
        self.pv_labels["pv_feel"].configure(text=f"{info['feels']}°C")

    # ─── SAVE METHODS ────────────────────────────
    def _save_weather_only(self):
        full = self.city_entry.get().strip()
        if not full:
            messagebox.showwarning("Advertencia" if self.lang_code == "es" else "Warning",
                self._tr("save_city_first"))
            return
        city = full.split(",")[0].strip()
        os.makedirs(os.path.dirname(ENV_PATH), exist_ok=True)
        set_key(ENV_PATH, "WEATHER_CITY", city)
        messagebox.showinfo(self._tr("config_title"), f"{self._tr('city_saved')} {city}")
        self._fetch_weather()

    def _save_single(self, section):
        if section == "api_model":
            k = self.api_key_entry.get()
            if not k:
                messagebox.showwarning("Advertencia" if self.lang_code == "es" else "Warning",
                    self._tr("api_empty_warn"))
                return
            set_key(ENV_PATH, "OLLAMA_API_KEY", k)
            self.ollama.set_api_key(k)
            tk = self.tavily_key_entry.get()
            set_key(ENV_PATH, "TAVILY_API_KEY", tk)
            m = self.model_var.get()
            t = str(self.temp_slider.get())
            set_key(ENV_PATH, "OLLAMA_MODEL", m)
            set_key(ENV_PATH, "OLLAMA_TEMPERATURE", t)
            messagebox.showinfo(self._tr("config_title"), self._tr("api_saved"))

    def _save_config_all(self):
        full = self.city_entry.get().strip()
        if full:
            city = full.split(",")[0].strip()
            set_key(ENV_PATH, "WEATHER_CITY", city)
        k = self.api_key_entry.get()
        if k:
            set_key(ENV_PATH, "OLLAMA_API_KEY", k)
        tk = self.tavily_key_entry.get()
        set_key(ENV_PATH, "TAVILY_API_KEY", tk)
        set_key(ENV_PATH, "OLLAMA_MODEL", self.model_var.get())
        set_key(ENV_PATH, "OLLAMA_TEMPERATURE", str(self.temp_slider.get()))
        messagebox.showinfo(self._tr("config_title"), self._tr("all_saved"))
        self._close_overlay()
        self._fetch_weather()

    def show_home(self):
        self._close_overlay()

    def show_mic_frame(self):
        self._close_overlay()

    def show_screen_frame(self):
        self._close_overlay()

    def show_pc_frame(self):
        self._close_overlay()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()
