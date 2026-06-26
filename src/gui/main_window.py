import customtkinter as ctk
from tkinter import messagebox, Canvas
import os, math, random
from dotenv import load_dotenv, set_key
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

ENV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
BG_COLOR = "#06080f"
PANEL_COLOR = "#0b0f1a"
BORDER_COLOR = "#1a2a44"
ACCENT = "#00bbff"
ACCENT_DIM = "#006688"
TEXT_DIM = "#557799"
TEXT_BRIGHT = "#88bbdd"


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
    kw = {"fg_color": PANEL_COLOR, "corner_radius": 10, "border_width": 1, "border_color": BORDER_COLOR}
    kw.update(kwargs)
    return ctk.CTkFrame(parent, **kw)


class MainWindow:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("ATLAS - Asistente Personal")
        self.window.geometry("1280x720")
        self.window.minsize(1100, 620)
        load_dotenv(ENV_PATH)
        self._build()

    def _build(self):
        # rows: topbar, main, bottom
        self.window.grid_rowconfigure(0, weight=0, minsize=44)
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_rowconfigure(2, weight=0, minsize=56)
        # columns: left, center, right
        self.window.grid_columnconfigure(0, weight=0, minsize=260)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_columnconfigure(2, weight=0, minsize=300)

        self._create_topbar()
        self._create_left_panels()
        self._create_center()
        self._create_right_panel()
        self._create_bottombar()

        # start animation
        self.anim = None
        self.canvas.after(100, self._start_anim)

    # ─── TOP BAR ─────────────────────────────────
    def _create_topbar(self):
        bar = ctk.CTkFrame(self.window, fg_color="#080b14", corner_radius=0, height=44)
        bar.grid(row=0, column=0, columnspan=3, sticky="ew", padx=0, pady=0)
        bar.grid_columnconfigure(2, weight=1)
        bar.grid_propagate(False)

        # logo
        frame_left = ctk.CTkFrame(bar, fg_color="transparent")
        frame_left.grid(row=0, column=0, padx=(16, 0), pady=0, sticky="w")
        ctk.CTkLabel(frame_left, text="A T L A S", font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(frame_left, text="  ●", font=ctk.CTkFont(size=12), text_color="#00cc44").pack(side="left", padx=(6, 0))
        ctk.CTkLabel(frame_left, text="Online", font=ctk.CTkFont(size=11), text_color="#44cc66").pack(side="left", padx=(3, 0))

        # center spacer (column 2 has weight=1)

        # right side info
        frame_right = ctk.CTkFrame(bar, fg_color="transparent")
        frame_right.grid(row=0, column=3, padx=(0, 16), pady=0, sticky="e")

        self._update_clock(frame_right)

        sep = ctk.CTkLabel(frame_right, text="|", text_color="#334466", font=ctk.CTkFont(size=14))
        sep.pack(side="left", padx=6)

        ctk.CTkLabel(frame_right, text="📅", font=ctk.CTkFont(size=12)).pack(side="left")
        self.date_lbl = ctk.CTkLabel(frame_right, text="", font=ctk.CTkFont(size=11), text_color=TEXT_DIM)
        self.date_lbl.pack(side="left", padx=(3, 10))
        self._update_date()

        ctk.CTkLabel(frame_right, text="🌤  25.2°C Querétaro", font=ctk.CTkFont(size=11),
            text_color=TEXT_DIM).pack(side="left", padx=(0, 10))

        self.gear_btn = ctk.CTkLabel(frame_right, text="⚙", font=ctk.CTkFont(size=16),
            text_color="#446688")
        self.gear_btn.pack(side="left")
        self.gear_btn.bind("<Button-1>", lambda e: self.show_config_frame())

        # schedule clock update
        self._clock_updater()

    def _update_clock(self, parent):
        if hasattr(self, 'clock_lbl'):
            self.clock_lbl.destroy()
        now = datetime.now()
        self.clock_lbl = ctk.CTkLabel(parent, text=f"🕐 {now.strftime('%I:%M:%S %p').lstrip('0')}",
            font=ctk.CTkFont(size=11), text_color=TEXT_DIM)
        self.clock_lbl.pack(side="left", padx=(0, 0))

    def _update_date(self):
        self.date_lbl.configure(text=datetime.now().strftime("%B %d, %Y"))

    def _clock_updater(self):
        now = datetime.now()
        if hasattr(self, 'clock_lbl'):
            self.clock_lbl.configure(text=f"🕐 {now.strftime('%I:%M:%S %p').lstrip('0')}")
        self.window.after(1000, self._clock_updater)

    # ─── LEFT PANELS ─────────────────────────────
    def _create_left_panels(self):
        container = ctk.CTkFrame(self.window, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=4)
        container.grid_rowconfigure((0, 1, 2, 3), weight=1, uniform="left")
        container.grid_columnconfigure(0, weight=1)

        self._panel_system(container, 0)
        self._panel_weather(container, 1)
        self._panel_camera(container, 2)
        self._panel_uptime(container, 3)

    def _panel_system(self, parent, row):
        p = glass_frame(parent)
        p.grid(row=row, column=0, sticky="nsew", padx=2, pady=2)
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(4, weight=1)

        hdr = ctk.CTkFrame(p, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=10, pady=(8, 0), sticky="ew")
        ctk.CTkLabel(hdr, text="System Stats", font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_BRIGHT).pack(side="left")
        ctk.CTkLabel(hdr, text="↻", font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(side="right")

        stats = [
            ("CPU Usage", "8%", 0.08),
            ("RAM Usage", "7 GB / 16 GB", 0.44),
        ]
        for i, (label, val, prog) in enumerate(stats):
            row_f = ctk.CTkFrame(p, fg_color="transparent")
            row_f.grid(row=1+i, column=0, padx=10, pady=(6, 0), sticky="ew")
            row_f.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(row_f, text=label, font=ctk.CTkFont(size=9), text_color=TEXT_DIM).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(row_f, text=val, font=ctk.CTkFont(size=9), text_color=TEXT_BRIGHT).grid(row=0, column=2, sticky="e")
            bar = ctk.CTkProgressBar(row_f, height=4, fg_color="#0a1a2a", progress_color=ACCENT, corner_radius=2)
            bar.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(2, 0))
            bar.set(prog)

        boxes = ctk.CTkFrame(p, fg_color="transparent")
        boxes.grid(row=3, column=0, padx=10, pady=(8, 6), sticky="ew")
        boxes.grid_columnconfigure((0, 1), weight=1)
        for i, (l, v) in enumerate([("CPU", "8%"), ("Memory", "44%")]):
            b = ctk.CTkFrame(boxes, fg_color="#0a1220", corner_radius=6)
            b.grid(row=0, column=i, sticky="ew", padx=2)
            ctk.CTkLabel(b, text=l, font=ctk.CTkFont(size=8), text_color=TEXT_DIM).pack()
            ctk.CTkLabel(b, text=v, font=ctk.CTkFont(size=10, weight="bold"), text_color=ACCENT).pack()

        disklbl = ctk.CTkLabel(p, text="Disk: 439 / 475 GB", font=ctk.CTkFont(size=9), text_color=TEXT_DIM)
        disklbl.grid(row=4, column=0, padx=10, pady=(4, 8), sticky="w")

    def _panel_weather(self, parent, row):
        p = glass_frame(parent)
        p.grid(row=row, column=0, sticky="nsew", padx=2, pady=2)
        p.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(p, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=10, pady=(6, 0), sticky="ew")
        ctk.CTkLabel(hdr, text="Weather", font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_BRIGHT).pack(side="left")
        ctk.CTkLabel(hdr, text="↻", font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(side="right")

        body = ctk.CTkFrame(p, fg_color="transparent")
        body.grid(row=1, column=0, padx=10, pady=4, sticky="ew")
        body.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(body, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(top, text="☁", font=ctk.CTkFont(size=28), text_color="#7799bb").pack(side="left", padx=(0, 8))
        ctk.CTkLabel(top, text="25.2°C", font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_BRIGHT).pack(side="left")
        ctk.CTkLabel(top, text="overcast\nclouds", font=ctk.CTkFont(size=8), text_color=TEXT_DIM).pack(side="right")

        ctk.CTkLabel(body, text="Querétaro, MX", font=ctk.CTkFont(size=9), text_color=TEXT_DIM).grid(row=1, column=0, sticky="w")

        mini = ctk.CTkFrame(body, fg_color="transparent")
        mini.grid(row=2, column=0, sticky="ew", pady=(4, 6))
        ctk.CTkLabel(mini, text="Humidity: 94%", font=ctk.CTkFont(size=8), text_color=TEXT_DIM).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(mini, text="Wind: 5.8 m/s", font=ctk.CTkFont(size=8), text_color=TEXT_DIM).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(mini, text="Feels: 26.3°C", font=ctk.CTkFont(size=8), text_color=TEXT_DIM).pack(side="left")

    def _panel_camera(self, parent, row):
        p = glass_frame(parent)
        p.grid(row=row, column=0, sticky="nsew", padx=2, pady=2)
        p.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(p, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=10, pady=(6, 0), sticky="ew")
        ctk.CTkLabel(hdr, text="Camera", font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_BRIGHT).pack(side="left")
        ctk.CTkLabel(hdr, text="📷  🖼  ⏻", font=ctk.CTkFont(size=10), text_color=TEXT_DIM).pack(side="right")

        cam_box = ctk.CTkFrame(p, fg_color="#040810", corner_radius=8, height=50)
        cam_box.grid(row=1, column=0, padx=10, pady=(8, 0), sticky="ew")
        cam_box.grid_propagate(False)
        ctk.CTkLabel(cam_box, text="📷", font=ctk.CTkFont(size=20), text_color="#334455").pack(expand=True)
        ctk.CTkLabel(p, text="Camera is inactive. Click the power button to start.",
            font=ctk.CTkFont(size=7), text_color=TEXT_DIM).grid(row=2, column=0, padx=10, pady=(4, 6))

    def _panel_uptime(self, parent, row):
        p = glass_frame(parent)
        p.grid(row=row, column=0, sticky="nsew", padx=2, pady=2)
        p.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(p, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=10, pady=(6, 0), sticky="ew")
        ctk.CTkLabel(hdr, text="System Uptime", font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_BRIGHT).pack(side="left")
        ctk.CTkLabel(hdr, text="00:07:19", font=ctk.CTkFont(size=9), text_color=TEXT_DIM).pack(side="right")

        ctk.CTkLabel(p, text="System Running For:", font=ctk.CTkFont(size=8), text_color=TEXT_DIM).grid(
            row=1, column=0, padx=10, pady=(4, 0), sticky="w")
        ctk.CTkLabel(p, text="00:07:19", font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ACCENT).grid(row=2, column=0, padx=10, sticky="w")

        boxes = ctk.CTkFrame(p, fg_color="transparent")
        boxes.grid(row=3, column=0, padx=10, pady=(4, 2), sticky="ew")
        boxes.grid_columnconfigure((0, 1), weight=1)
        for i, (l, v) in enumerate([("Session", "1"), ("Commands", "0")]):
            b = ctk.CTkFrame(boxes, fg_color="#0a1220", corner_radius=6)
            b.grid(row=0, column=i, sticky="ew", padx=2)
            ctk.CTkLabel(b, text=l, font=ctk.CTkFont(size=8), text_color=TEXT_DIM).pack()
            ctk.CTkLabel(b, text=v, font=ctk.CTkFont(size=10, weight="bold"), text_color=ACCENT).pack()

        load_f = ctk.CTkFrame(p, fg_color="transparent")
        load_f.grid(row=4, column=0, padx=10, pady=(4, 8), sticky="ew")
        load_f.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(load_f, text="System Load:", font=ctk.CTkFont(size=8), text_color=TEXT_DIM).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(load_f, text="Moderate 26%", font=ctk.CTkFont(size=8), text_color=TEXT_DIM).grid(row=0, column=2, sticky="e")
        bar = ctk.CTkProgressBar(load_f, height=4, fg_color="#0a1a2a", progress_color="#ffaa00", corner_radius=2)
        bar.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(2, 0))
        bar.set(0.26)

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
            font=ctk.CTkFont(size=26, weight="bold"), text_color=ACCENT)
        self.title_lbl.pack()

        status_f = ctk.CTkFrame(overlay, fg_color="transparent")
        status_f.pack(pady=(4, 0))
        ctk.CTkLabel(status_f, text="●", font=ctk.CTkFont(size=10), text_color="#00cc44").pack(side="left", padx=(0, 4))
        ctk.CTkLabel(status_f, text="Listening for wake word...",
            font=ctk.CTkFont(size=10), text_color=TEXT_DIM).pack(side="left")

        # collapsible left tab mock
        tab = ctk.CTkLabel(center, text="◀", font=ctk.CTkFont(size=10),
            fg_color="#2a1a44", text_color="#9966ff", corner_radius=4, width=14, height=30)
        tab.place(relx=0, rely=0.5, anchor="w")

    def _on_resize(self, e):
        if hasattr(self, 'anim') and self.anim:
            self.anim.w = e.width
            self.anim.h = e.height
            self.anim.cx = e.width // 2
            self.anim.cy = e.height // 2

    def _start_anim(self):
        w = self.canvas.winfo_width() or 400
        h = self.canvas.winfo_height() or 400
        self.anim = AtlasAnim(self.canvas, w, h)
        self.anim.draw()

    # ─── RIGHT PANEL ─────────────────────────────
    def _create_right_panel(self):
        p = glass_frame(self.window)
        p.grid(row=1, column=2, sticky="nsew", padx=(4, 8), pady=4)
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(2, weight=1)

        hdr = ctk.CTkFrame(p, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=10, pady=(10, 4), sticky="ew")
        ctk.CTkLabel(hdr, text="Conversation", font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_BRIGHT).pack(side="left")
        ctk.CTkLabel(hdr, text="🗑  ⬇", font=ctk.CTkFont(size=10), text_color=TEXT_DIM).pack(side="right")

        chat_area = ctk.CTkFrame(p, fg_color="#060a14", corner_radius=8)
        chat_area.grid(row=2, column=0, padx=10, pady=4, sticky="nsew")
        chat_area.grid_columnconfigure(0, weight=1)
        chat_area.grid_rowconfigure(1, weight=1)

        bubble = ctk.CTkFrame(chat_area, fg_color="#0c1428", corner_radius=8)
        bubble.grid(row=0, column=0, padx=6, pady=(6, 2), sticky="ew")
        bubble.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(bubble,
            text="Hello, I am ATLAS.\nBackend is offline.\nSome features may be limited.\nHow can I assist you today, sir?",
            font=ctk.CTkFont(size=9), text_color=TEXT_BRIGHT, justify="left", wraplength=240).grid(
            row=0, column=0, padx=8, pady=8, sticky="w")
        ctk.CTkLabel(p, text="2:45 PM", font=ctk.CTkFont(size=8), text_color=TEXT_DIM).grid(
            row=3, column=0, padx=16, pady=(0, 6), sticky="w")

    # ─── BOTTOM BAR ──────────────────────────────
    def _create_bottombar(self):
        bar = ctk.CTkFrame(self.window, fg_color="#080b14", corner_radius=0, height=56)
        bar.grid(row=2, column=0, columnspan=3, sticky="ew", padx=0, pady=0)
        bar.grid_propagate(False)

        content = ctk.CTkFrame(bar, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        # mode icons
        for icon in ["🎥", "🎤", "⌨️"]:
            lbl = ctk.CTkLabel(content, text=icon, font=ctk.CTkFont(size=14), text_color=TEXT_DIM)
            lbl.pack(side="left", padx=4)

        # input field
        self.entry = ctk.CTkEntry(content, width=400, height=32,
            fg_color="#0a1220", border_color="#1a2a44", text_color=TEXT_BRIGHT,
            placeholder_text="Type a message...")
        self.entry.pack(side="left", padx=(10, 6))

        send = ctk.CTkLabel(content, text="📤", font=ctk.CTkFont(size=16), text_color=TEXT_DIM)
        send.pack(side="left")

        # floating button bottom right
        float_btn = ctk.CTkLabel(bar, text="⚙", font=ctk.CTkFont(size=14),
            fg_color="#2a1a44", text_color="#9966ff", corner_radius=20, width=32, height=32)
        float_btn.place(relx=1, rely=1, anchor="se", x=-12, y=-8)

    # ─── CONTENT PANELS (Config, etc) ────────────
    def _make_overlay(self):
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.destroy()
        self.overlay = ctk.CTkFrame(self.window, fg_color="#060a14")
        self.overlay.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=40, pady=20)
        self.overlay.grid_columnconfigure(0, weight=1)
        self.overlay.grid_rowconfigure(10, weight=1)
        return self.overlay

    def _close_overlay(self, e=None):
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.destroy()
            self.overlay = None

    def show_config_frame(self):
        parent = self._make_overlay()

        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        ctk.CTkLabel(top, text="⚙ Configuración", font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(top, text="✕", font=ctk.CTkFont(size=16), text_color=TEXT_DIM).pack(side="right")
        top.bind("<Button-1>", self._close_overlay)

        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")
        f.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(f, text="API Key de Ollama Cloud:").grid(row=0, column=0, pady=5, sticky="w")
        self.api_key_entry = ctk.CTkEntry(f, width=380, show="*")
        self.api_key_entry.grid(row=1, column=0, pady=(0, 10), sticky="w")
        saved = os.getenv("OLLAMA_API_KEY", "")
        if saved:
            self.api_key_entry.insert(0, saved)

        ctk.CTkLabel(f, text="Modelo:").grid(row=2, column=0, pady=5, sticky="w")
        self.model_var = ctk.StringVar(value=os.getenv("OLLAMA_MODEL", "llama3"))
        self.model_menu = ctk.CTkOptionMenu(f, values=["llama3", "mistral", "codellama", "gemma", "phi"],
            variable=self.model_var, fg_color="#0a1a33", button_color="#004466")
        self.model_menu.grid(row=3, column=0, pady=(0, 10), sticky="w")

        ctk.CTkLabel(f, text="Temperatura (0.0 - 1.0):").grid(row=4, column=0, pady=5, sticky="w")
        tf = ctk.CTkFrame(f, fg_color="transparent")
        tf.grid(row=5, column=0, pady=5, sticky="w")
        self.temp_slider = ctk.CTkSlider(tf, from_=0, to=1, number_of_steps=20,
            fg_color="#112244", progress_color=ACCENT, button_color="#0088cc")
        self.temp_slider.pack(side="left")
        self.temp_slider.set(float(os.getenv("OLLAMA_TEMPERATURE", "0.7")))
        self.temp_label = ctk.CTkLabel(tf, text=f"{self.temp_slider.get():.1f}")
        self.temp_label.pack(side="left", padx=(10, 0))
        self.temp_slider.configure(command=lambda v: self.temp_label.configure(text=f"{v:.1f}"))

        ctk.CTkButton(f, text="💾 Guardar configuración", command=self._save_config,
            fg_color="#004466", hover_color="#006688", corner_radius=8, width=200
        ).grid(row=6, column=0, padx=0, pady=20, sticky="w")

    def _save_config(self):
        k = self.api_key_entry.get()
        m = self.model_var.get()
        t = str(self.temp_slider.get())
        if not k:
            messagebox.showwarning("Advertencia", "La API Key no puede estar vacía.")
            return
        os.makedirs(os.path.dirname(ENV_PATH), exist_ok=True)
        set_key(ENV_PATH, "OLLAMA_API_KEY", k)
        set_key(ENV_PATH, "OLLAMA_MODEL", m)
        set_key(ENV_PATH, "OLLAMA_TEMPERATURE", t)
        messagebox.showinfo("Guardado", "Configuración guardada correctamente.")

    # placeholder methods for sidebar nav compatibility
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
