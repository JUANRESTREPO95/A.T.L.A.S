import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

FETCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "es-ES,es;q=0.9",
}


def _fetch_page_text(url: str, max_chars: int = 3000) -> str | None:
    try:
        r = requests.get(url, headers=FETCH_HEADERS, timeout=8)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        text = " ".join(text.split())
        return text[:max_chars] if len(text) > 100 else None
    except Exception:
        return None


def search_web(query: str, tavily_api_key: str | None = None, max_results: int = 5) -> str | None:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results * 2))
            if not results:
                return None
    except Exception:
        return None

    lines = []
    seen_titles = set()

    for r in results[:max_results]:
        title = (r.get("title") or "").strip()
        body = (r.get("body") or r.get("snippet") or "").strip()
        url = (r.get("url") or r.get("href") or "").strip()

        if not title or title in seen_titles:
            continue
        seen_titles.add(title)

        lines.append(f"• {title}")
        if body:
            lines.append(f"  {body[:500]}")

        page_text = _fetch_page_text(url) if url else None
        if page_text:
            lines.append(f"  [Contenido extraído]: {page_text}")

        if url:
            lines.append(f"  Fuente: {url}")
        lines.append("")

    text = "\n".join(lines).strip()
    return text if text else None
