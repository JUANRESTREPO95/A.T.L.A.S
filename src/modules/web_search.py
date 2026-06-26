from ddgs import DDGS


def search_web(query, max_results=5):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                results = list(ddgs.news(query, max_results=max_results))
            if not results:
                return None
            return _format_results(results)
    except Exception:
        return None


def _format_results(results):
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
