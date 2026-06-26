import requests
from urllib.parse import quote_plus

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def search_web(query, max_results=5):
    try:
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None

        results = _parse_results(resp.text, max_results)
        return _format_results(results) if results else None
    except Exception:
        return None


def search_instant(query):
    try:
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code != 200:
            return None

        data = resp.json()
        parts = []

        abstract = data.get("AbstractText", "")
        if abstract:
            parts.append(abstract)

        answer = data.get("Answer", "")
        if answer and answer != abstract:
            parts.append(answer)

        definition = data.get("Definition", "")
        if definition:
            parts.append(definition)

        return "\n".join(parts) if parts else None
    except Exception:
        return None


def _parse_results(html, max_results):
    import re
    results = []
    for match in re.finditer(
        r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?'
        r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
        html, re.DOTALL
    ):
        url = match.group(1)
        title = re.sub(r"<[^>]+>", "", match.group(2)).strip()
        snippet = re.sub(r"<[^>]+>", "", match.group(3)).strip()
        results.append((title, url, snippet))
        if len(results) >= max_results:
            break

    if not results:
        results = _parse_fallback(html, max_results)
    return results


def _parse_fallback(html, max_results):
    import re
    results = []
    for match in re.finditer(
        r'<a[^>]*class="result__a"[^>]*>(.*?)</a>',
        html, re.DOTALL
    ):
        title = re.sub(r"<[^>]+>", "", match.group(1)).strip()
        snippet_match = re.search(
            r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
            html[match.end():], re.DOTALL
        )
        snippet = re.sub(r"<[^>]+>", "", snippet_match.group(1)).strip() if snippet_match else ""
        results.append((title, "", snippet))
        if len(results) >= max_results:
            break
    return results


def _format_results(results):
    lines = []
    for title, url, snippet in results:
        lines.append(f"- {title}")
        if snippet:
            lines.append(f"  {snippet}")
        if url:
            lines.append(f"  Fuente: {url}")
        lines.append("")
    return "\n".join(lines).strip()
