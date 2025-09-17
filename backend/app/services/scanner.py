import requests
from bs4 import BeautifulSoup
import traceback

def passive_scan_url(url: str) -> dict:
    """
    Passive scan that fetches URL and returns:
    - status_code, headers
    - count of forms, scripts
    - presence of CSP header, cookies
    - a tiny html snippet
    """
    try:
        resp = requests.get(url, timeout=8, allow_redirects=True, headers={"User-Agent": "BountyHunterAI/1.0"})
    except Exception as e:
        return {"error": "fetch_failed", "error_msg": str(e)}

    result = {
        "url": url,
        "status_code": resp.status_code,
        "headers": dict(resp.headers),
        "csp": resp.headers.get("Content-Security-Policy"),
        "cookies": resp.cookies.get_dict(),
    }
    text = resp.text or ""
    soup = BeautifulSoup(text, "html.parser")
    forms = soup.find_all("form")
    scripts = soup.find_all("script")
    result.update({
        "forms_count": len(forms),
        "scripts_count": len(scripts),
        "title": soup.title.string.strip() if soup.title and soup.title.string else None,
        "html_snippet": text[:4000],
    })
    # basic heuristics
    suspicious = []
    if not result["csp"]:
        suspicious.append("missing_csp")
    for s in scripts:
        src = s.get("src")
        if not src:
            # inline script
            suspicious.append("inline_script")
            break
    result["suspicious"] = list(set(suspicious))
    return result

def passive_scan_urls(urls: list) -> dict:
    results = {}
    for u in urls:
        try:
            results[u] = passive_scan_url(u)
        except Exception:
            results[u] = {"error": "unexpected", "trace": traceback.format_exc()[:2000]}
    return results