import requests
from ddgs import DDGS

BRAVE_URL = "https://api.search.brave.com/res/v1/web/search"


def brave_search(query, api_key, max_results=5):
    try:
        resp = requests.get(BRAVE_URL, headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key,
        }, params={"q": query, "count": max_results}, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        results = []
        for item in (data.get("web", {}) or {}).get("results", []):
            title = (item.get("title") or "").strip()
            desc = (item.get("description") or "").strip()
            url = (item.get("url") or "").strip()
            if title:
                results.append({"title": title, "body": desc, "url": url})
        return _fmt(results) if results else None
    except Exception:
        return None


def _gen_queries(query):
    q = query.lower()
    base = [query]
    if "hoy" not in q and "today" not in q:
        base.append(query + " hoy")
        base.append(query + " today")
    if "mundial" in q or "world cup" in q or "copa" in q:
        base.append("partidos mundial 2026 hoy")
        base.append("World Cup 2026 matches today")
        base.append("Copa Mundial 2026 calendario partidos")
        base.append("fifa world cup 2026 schedule fixtures")
    if "clima" in q or "weather" in q or "temperatura" in q or "lluvia" in q:
        base.append("clima hoy")
        base.append("weather today")
    if not any(w in q for w in ("noticia", "news", "último", "latest", "actualidad", "reciente")):
        base.append("últimas noticias " + query)
        base.append("latest news " + query)
    return base


def search_web(query, brave_api_key=None, max_results=5):
    if brave_api_key:
        r = brave_search(query, brave_api_key, max_results)
        if r:
            return r

    try:
        queries = _gen_queries(query)
        seen = set()
        all_results = []
        with DDGS() as ddgs:
            for q in queries:
                try:
                    results = list(ddgs.text(q, max_results=max_results))
                    if not results:
                        results = list(ddgs.news(q, max_results=max_results))
                    for r in results:
                        title = r.get("title", "").strip()
                        if not title or title in seen:
                            continue
                        seen.add(title)
                        all_results.append(r)
                except Exception:
                    continue
                if len(all_results) >= max_results * 2:
                    break
        if not all_results:
            return None
        return _fmt(all_results[:max_results * 2])
    except Exception:
        return None


def _fmt(results):
    lines = []
    for r in results:
        title = r.get("title", "").strip()
        body = r.get("body", "") or r.get("snippet", "")
        url = r.get("url", "") or r.get("href", "")
        if not title:
            continue
        lines.append(f"• {title}")
        if body:
            lines.append(f"  {body[:400]}")
        if url:
            lines.append(f"  Fuente: {url}")
        lines.append("")
    text = "\n".join(lines).strip()
    return text if text else None
