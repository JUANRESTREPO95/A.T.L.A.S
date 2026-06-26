from ddgs import DDGS
from tavily import TavilyClient


def tavily_search(query, api_key):
    try:
        client = TavilyClient(api_key=api_key)
        resp = client.search(query, search_depth="advanced", max_results=5)
        results = resp.get("results", [])
        if not results:
            return None
        lines = []
        for r in results:
            title = (r.get("title") or "").strip()
            content = (r.get("content") or "").strip()
            url = (r.get("url") or "").strip()
            if not title:
                continue
            lines.append(f"• {title}")
            if content:
                lines.append(f"  {content[:600]}")
            if url:
                lines.append(f"  Fuente: {url}")
            lines.append("")
        text = "\n".join(lines).strip()
        return text if text else None
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


def search_web(query, tavily_api_key=None, max_results=5):
    if tavily_api_key:
        r = tavily_search(query, tavily_api_key)
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
