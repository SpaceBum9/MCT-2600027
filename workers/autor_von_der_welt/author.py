#!/usr/bin/env python3
"""
Autor von der Welt — RSS impulse → Gemini briefing → MCT ATM envelope → Sheet worker.
Secrets and the web-app URL stay in the environment. Never committed.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any

import feedparser
import requests
from google import genai

RSS_FEED_URL = os.getenv(
    "MCT_RSS_URL",
    "https://news.google.com/rss?hl=de&gl=DE&ceid=DE:de",
)
NODE = os.getenv("MCT_NODE", "AUTOR_VON_DER_WELT")
MODEL = os.getenv("MCT_GEMINI_MODEL", "gemini-2.5-flash")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def fetch_latest_world_signal() -> str:
    feed = feedparser.parse(RSS_FEED_URL)
    top_entries = feed.entries[:5]
    if not top_entries:
        raise RuntimeError(f"empty RSS feed: {RSS_FEED_URL}")
    return "\n".join(
        f"- {entry.title}: {getattr(entry, 'link', '')}" for entry in top_entries
    )


def write_world_article(news_data: str, api_key: str) -> str:
    client = genai.Client(api_key=api_key)
    prompt = f"""
Du bist der 'Autor von der Welt'. Analysiere die folgenden aktuellen Impulse und erstelle
einen klaren, prägnanten Kurzbericht (max. 200 Wörter) mit dem Titel 'Welt-Signal Briefing'.

Impulse:
{news_data}
""".strip()
    response = client.models.generate_content(model=MODEL, contents=prompt)
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned empty briefing")
    return text


def stamp_envelope(title: str, article_text: str, news_data: str) -> dict[str, Any]:
    utc = utc_now()
    body = {
        "atm": "MCT_ATM",
        "grade": "GOLD",
        "payload_type": "AUTHOR_SIGNAL",
        "node": NODE,
        "title": title,
        "content": article_text,
        "phase_angle": 0.0,
        "utc": utc,
        "source": RSS_FEED_URL,
        "impulse": news_data,
    }
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    body["watermark"] = "wm_" + digest[:32]
    body["trace_id"] = body["watermark"]
    return body


def dispatch_to_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    url = os.getenv("MCT_TELEMETRY_URL", "").strip()
    if not url or "YOUR_DEPLOYMENT_ID" in url:
        return {
            "status": "skipped",
            "reason": "no_url",
            "claims_external_delivery": False,
        }

    body = dict(payload)
    token = os.getenv("MCT_WEBHOOK_TOKEN", "").strip()
    if token:
        body["token"] = token

    res = requests.post(
        url,
        data=json.dumps(body, separators=(",", ":")),
        headers={"Content-Type": "application/json"},
        timeout=20,
        allow_redirects=True,
    )
    parsed: Any
    try:
        parsed = res.json()
    except ValueError:
        parsed = res.text[:500]
    ok = 200 <= res.status_code < 300
    return {
        "status": "SUCCESS" if ok else "ERROR",
        "http_status": res.status_code,
        "body": parsed,
        "claims_external_delivery": ok,
    }


def main() -> int:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("author: GEMINI_API_KEY missing", file=sys.stderr)
        return 2

    print("Fetching world signals...")
    raw_news = fetch_latest_world_signal()

    print("Drafting article...")
    article = write_world_article(raw_news, api_key)

    payload = stamp_envelope("Welt-Signal Briefing", article, raw_news)
    print(json.dumps({"watermark": payload["watermark"], "utc": payload["utc"]}, indent=2))
    print(article)

    print("Publishing to Workspace...")
    result = dispatch_to_workspace(payload)
    print("Google Workspace Sync Result:", json.dumps(result, ensure_ascii=False))
    return 0 if result.get("status") in {"SUCCESS", "skipped"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
