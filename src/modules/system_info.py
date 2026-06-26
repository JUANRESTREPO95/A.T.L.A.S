import os
import re
import psutil
from datetime import datetime

HOME = os.path.expanduser("~")
PROJECT_ROOTS = [
    os.path.join(HOME, "Proyectos"),
    os.path.join(HOME, "projects"),
    os.path.join(HOME, "Escritorio"),
    os.path.join(HOME, "Desktop"),
    os.path.join(HOME, "Documentos"),
    os.path.join(HOME, "Documents"),
]


def get_cpu_info() -> str:
    return (
        f"CPU: {psutil.cpu_percent(interval=0)}% usado, "
        f"{psutil.cpu_count()} núcleos lógicos"
    )


def get_ram_info() -> str:
    mem = psutil.virtual_memory()
    used_gb = mem.used / (1024**3)
    total_gb = mem.total / (1024**3)
    return f"RAM: {used_gb:.1f} GB / {total_gb:.1f} GB ({mem.percent}% usado)"


def get_disk_info() -> str:
    parts = []
    for part in psutil.disk_partitions():
        if part.mountpoint.startswith("/snap"):
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            if total_gb > 1:
                parts.append(
                    f"  {part.mountpoint}: {used_gb:.1f} GB / {total_gb:.1f} GB "
                    f"({usage.percent}% usado)"
                )
        except PermissionError:
            continue
    return "Disco:\n" + "\n".join(parts) if parts else ""


def get_process_list(count: int = 15) -> str:
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: -(x["memory_percent"] or 0))
    lines = [f"Top {count} procesos por uso de RAM:"]
    for p in procs[:count]:
        lines.append(
            f"  PID {p['pid']:>6}  {p['name'][:30]:<30}  "
            f"CPU {p['cpu_percent'] or 0:.1f}%  "
            f"RAM {p['memory_percent'] or 0:.1f}%"
        )
    return "\n".join(lines)


def get_projects() -> str:
    found = []
    for root in PROJECT_ROOTS:
        if not os.path.isdir(root):
            continue
        try:
            for entry in sorted(os.listdir(root)):
                full = os.path.join(root, entry)
                if os.path.isdir(full):
                    found.append(f"  • {entry}  ({full})")
        except PermissionError:
            continue
    if not found:
        return "No se encontraron proyectos."
    return "Proyectos locales:\n" + "\n".join(found)


def get_file_list(path: str, max_items: int = 30) -> str:
    if not os.path.exists(path):
        return f"'{path}' no existe."
    try:
        entries = os.listdir(path)
    except PermissionError:
        return f"Sin permiso para leer '{path}'."
    dirs = []
    files = []
    for e in sorted(entries):
        full = os.path.join(path, e)
        if os.path.isdir(full):
            dirs.append(f"  📁 {e}/")
        else:
            size = os.path.getsize(full)
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024**2:
                size_str = f"{size/1024:.0f} KB"
            else:
                size_str = f"{size/1024**2:.1f} MB"
            files.append(f"  📄 {e}  ({size_str})")
    total = dirs + files
    if len(total) > max_items:
        total = total[:max_items]
        total.append(f"  ... y {len(entries) - max_items} más")
    return f"Contenido de {path}:\n" + "\n".join(total) if total else f"{path} está vacío."


def get_home_structure(depth: int = 1) -> str:
    lines = [f"Estructura de ~ ({HOME}):"]
    try:
        for entry in sorted(os.listdir(HOME)):
            full = os.path.join(HOME, entry)
            if entry.startswith("."):
                continue
            if os.path.isdir(full):
                lines.append(f"  📁 {entry}/")
            else:
                size = os.path.getsize(full)
                lines.append(f"  📄 {entry}  ({size/1024:.0f} KB)" if size > 1024 else f"  📄 {entry}")
    except PermissionError:
        lines.append("  (sin permiso)")
    return "\n".join(lines)


def get_network_info() -> str:
    net = psutil.net_io_counters()
    sent_mb = net.bytes_sent / (1024**2)
    recv_mb = net.bytes_recv / (1024**2)
    return f"Red: {sent_mb:.0f} MB enviados, {recv_mb:.0f} MB recibidos (sesión actual)"


def get_system_summary() -> str:
    boot = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot
    days = uptime.days
    hours = uptime.seconds // 3600
    mins = (uptime.seconds % 3600) // 60
    return (
        f"Sistema: {os.uname().sysname} {os.uname().release}\n"
        f"Hostname: {os.uname().nodename}\n"
        f"Usuario: {os.getlogin()}\n"
        f"Activo desde: {boot.strftime('%d/%m/%Y %H:%M')} ({days}d {hours}h {mins}m)\n"
        f"{get_cpu_info()}\n"
        f"{get_ram_info()}"
    )


# ─── Query router ────────────────────────────────

PC_KEYWORDS = [
    r"ram|memoria|disco|disco duro|almacenamiento|procesador|cpu|kernel",
    r"procesos|programas\s+abiertos|ejecutando|corriendo|top",
    r"archivos|ficheros|carpetas|directorios",
    r"descargas|documentos|escritorio|home|usuario",
    r"proyectos|projectos|repos|repositorios",
    r"red|internet|wifi|conexión|network|ip",
    r"sistema|pc|computador|computadora|ordenador|equipo",
    r"ollama|tokens|api\s*key",
]


def detect_pc_query(query: str) -> bool:
    q = query.lower()
    for pattern in PC_KEYWORDS:
        if re.search(pattern, q):
            return True
    return False


def get_pc_context(query: str) -> str | None:
    q = query.lower()
    parts = []

    if any(w in q for w in ["ram", "memoria"]):
        parts.append(get_ram_info())
    if any(w in q for w in ["cpu", "procesador"]):
        parts.append(get_cpu_info())
    if any(w in q for w in ["disco", "almacenamiento"]):
        parts.append(get_disk_info())
    if any(w in q for w in ["procesos", "ejecutando", "corriendo", "top", "abiertos"]):
        parts.append(get_process_list())
    if any(w in q for w in ["proyectos", "projectos", "repos"]):
        parts.append(get_projects())
    if any(w in q for w in ["archivos", "ficheros", "carpetas", "directorios"]):
        # Find which directory - check for "descargas", "documentos", etc.
        target = HOME
        for d, keyword in [
            ("Descargas", "descarga"),
            ("Downloads", "download"),
            ("Documentos", "documento"),
            ("Documents", "documents"),
            ("Escritorio", "escritorio"),
            ("Desktop", "desktop"),
            ("Proyectos", "proyecto"),
            ("projects", "project"),
        ]:
            if keyword in q:
                candidate = os.path.join(HOME, d)
                if os.path.isdir(candidate):
                    target = candidate
                    break
        parts.append(get_file_list(target))
    if any(w in q for w in ["red", "internet", "conexion", "network", "wifi"]):
        parts.append(get_network_info())
    if any(w in q for w in ["sistema", "pc", "computador", "equipo", "computadora", "ordenador"]):
        parts.append(get_system_summary())

    if not parts:
        parts.append(get_system_summary())
        parts.append(get_disk_info())
        parts.append(get_projects())

    return "\n\n".join(parts)
