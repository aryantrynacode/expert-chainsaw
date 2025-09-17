import os
import json
from . import scanner
from ..config import settings

# Try openai if key present
try:
    import openai
    if settings.OPENAI_API_KEY:
        openai.api_key = settings.OPENAI_API_KEY
    else:
        openai = None
except Exception:
    openai = None

def _prompt_for_analysis(scan_data, extra_text=None):
    # Build a prompt instructing the model to return JSON only
    short = {
        "urls_scanned": list(scan_data.keys()),
        "summary_for_each": {u: {"status_code": scan_data[u].get("status_code"), "suspicious": scan_data[u].get("suspicious")} for u in scan_data}
    }
    prompt = f"""
You are a security triage assistant. Given the below passive scan data (headers, snippet, forms_count, scripts_count, suspicious indicators),
return for each URL a JSON object with fields:
title, description, location, severity (Low/Medium/High/Critical), ai_confidence (0-1), evidence (list), suggested_steps (list).

SCAN_DATA:
{json.dumps(short, indent=2)}

If you are uncertain, set ai_confidence to a low value (<0.6) and include suggested_steps for manual verification.
Return ONLY valid JSON mapping URL -> analysis.
"""
    if extra_text:
        prompt += "\n\nEXTRA_TEXT:\n" + extra_text
    return prompt

def analyze_with_openai(scan_data, extra_text=None):
    prompt = _prompt_for_analysis(scan_data, extra_text)
    # Use ChatCompletion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system", "content":"You are a security triage assistant that returns JSON only."},
            {"role":"user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=800
    )
    out = response.choices[0].message.content
    # The model should output JSON; attempt to parse
    try:
        parsed = json.loads(out)
    except Exception:
        # If parsing fails, wrap fallback
        parsed = {"error": "openai_json_parse_failed", "raw": out}
    return parsed

def heuristic_analyze(scan_data, extra_text=None):
    """
    Simple fallback: if html_snippet contains '<script' or 'on' attributes -> XSS suspicion.
    If headers show old libs -> mark informative.
    """
    analyses = {}
    for url, data in scan_data.items():
        if "error" in data:
            analyses[url] = {
                "title": "Fetch failed",
                "description": data.get("error_msg", "Could not fetch URL"),
                "location": url,
                "severity": "Low",
                "ai_confidence": 0.2,
                "evidence": [data.get("error", "")],
                "suggested_steps": ["Manually inspect the URL."]
            }
            continue

        snippet = (data.get("html_snippet") or "").lower()
        findings = []
        if "<script" in snippet or "onerror=" in snippet or "onclick=" in snippet:
            findings.append("possible_xss_reflection")
        if not data.get("csp"):
            findings.append("missing_csp")
        severity = "Medium" if "possible_xss_reflection" in findings else "Low"
        confidence = 0.7 if findings else 0.3
        analyses[url] = {
            "title": "Potential issue detected" if findings else "No obvious issues",
            "description": " & ".join(findings) if findings else "No suspicious automated signals found in passive scan.",
            "location": url,
            "severity": severity,
            "ai_confidence": confidence,
            "evidence": findings,
            "suggested_steps": ["Manually verify by testing input reflection", "Check CSP and sanitize user input"]
        }
    return analyses

def analyze_scan(scan_data, extra_text=None):
    """
    Main analyzer function:
    - If OpenAI configured, use it.
    - Else fallback to heuristic analyze.
    """
    if openai:
        try:
            parsed = analyze_with_openai(scan_data, extra_text)
            # If parsing returned mapping per URL, return directly
            if isinstance(parsed, dict):
                return parsed
            # fallback
        except Exception:
            pass
    # fallback heuristic
    return heuristic_analyze(scan_data, extra_text)