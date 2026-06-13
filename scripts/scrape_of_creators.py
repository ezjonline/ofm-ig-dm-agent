#!/usr/bin/env python3
"""
Scrape OnlyFans creator leads via Apify (sentry/onlyfans-model-leads-scraper),
flag likely OFM-agency-managed profiles, and write a campaign-ready CSV.

Funnel:
  niche keyword -> OF model profiles (with IG link + follower count + pricing)
                -> regex pass over bio/socials for "managed by @xyz" OFM signals
                -> CSV of leads, OFM-signal rows surfaced first

Cost: Apify pay-per-event, ~$0.02 per profile returned. A 50-profile run is ~$1
on the prepaid APIFY_API_TOKEN. Keep --max small while validating.

Usage:
  python3 scripts/scrape_of_creators.py --niche fitness --max 25
  python3 scripts/scrape_of_creators.py --niche alt --max 50 --max-likes 500
"""
import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ACTOR = "sentry~onlyfans-model-leads-scraper"
API = "https://api.apify.com/v2"

# Load APIFY_API_TOKEN from the documented secret locations.
ENV_PATHS = [
    Path.home() / ".claude-secrets" / "ofm-ig-dm-agent" / ".env",
    Path.home() / ".claude-secrets" / "claudia" / ".env",
    Path(__file__).resolve().parent.parent / ".env",
]


def load_token():
    tok = os.environ.get("APIFY_API_TOKEN")
    if tok:
        return tok
    for p in ENV_PATHS:
        if p.exists():
            for line in p.read_text().splitlines():
                if line.startswith("APIFY_API_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("APIFY_API_TOKEN not found in env or secret files.")


def api_call(method, url, token, payload=None):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.request(method, url, headers=headers, json=payload, timeout=60)
    if not r.ok:
        sys.exit(f"Apify API error {r.status_code}: {r.text[:300]}")
    return r.json()


# Positive OFM-management signals in a creator's bio or socials.
OFM_PATTERNS = [
    re.compile(r"managed by\s*@?[\w.]+", re.I),
    re.compile(r"management[:\s]+@?[\w.]+", re.I),
    re.compile(r"mgmt[:\s]+@?[\w.]+", re.I),
    re.compile(r"booking[s]?[:\s]+@?[\w.]+", re.I),
    re.compile(r"represented by\s*@?[\w.]+", re.I),
    re.compile(r"@[\w.]+\s+(?:management|agency|mgmt)", re.I),
]
# Phrases that mean the creator is explicitly INDEPENDENT. Kills false positives
# like "no i don't want to join your agency".
INDEP_PATTERNS = [
    re.compile(r"(?:don't|dont|do not|no)[^.]{0,30}\bagency\b", re.I),
    re.compile(r"\b(?:not managed|independent|no management|self.?managed)\b", re.I),
]


def ofm_signal(text):
    if not text:
        return ""
    for neg in INDEP_PATTERNS:
        if neg.search(text):
            return "INDEPENDENT"
    hits = []
    for pat in OFM_PATTERNS:
        m = pat.search(text)
        if m:
            hits.append(m.group(0).strip())
    return " | ".join(dict.fromkeys(hits))


def first_present(d, keys):
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return ""


def normalize(items):
    """Map raw actor records to stable lead rows, OFM-signal + IG rows surfaced first."""
    rows = []
    for it in items:
        bio = it.get("bio", "") or ""
        rows.append({
            "of_username": it.get("onlyfansUsername", ""),
            "of_url": it.get("onlyfansLink", ""),
            "price": it.get("price", ""),
            "instagram": it.get("primaryInstagram", ""),
            "ig_handle": it.get("primaryInstagramUsername", ""),
            "twitter": (it.get("twitterLinks") or [{}])[0].get("url", "") if it.get("twitterLinks") else "",
            "tiktok": (it.get("tiktokLinks") or [{}])[0].get("url", "") if it.get("tiktokLinks") else "",
            "likes": it.get("likes", ""),
            "photos": it.get("photos", ""),
            "last_seen": it.get("lastSeen", ""),
            "bio": bio[:500],
            "ofm_signal": ofm_signal(bio),
        })
    # Managed leads first, then INDEPENDENT last, then by username.
    def rank(r):
        s = r["ofm_signal"]
        return (0 if s and s != "INDEPENDENT" else (2 if s == "INDEPENDENT" else 1), r["of_username"])
    rows.sort(key=rank)
    return rows


def write_outputs(rows, items, niche):
    out_dir = Path(__file__).resolve().parent.parent / "leads"
    out_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    tag = (niche or "any").replace(" ", "_")
    csv_path = out_dir / f"of_leads_{tag}_{stamp}.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    if items is not None:
        (out_dir / f"of_leads_{tag}_{stamp}_raw.json").write_text(json.dumps(items, indent=2))
    managed = sum(1 for r in rows if r["ofm_signal"] and r["ofm_signal"] != "INDEPENDENT")
    indep = sum(1 for r in rows if r["ofm_signal"] == "INDEPENDENT")
    with_ig = sum(1 for r in rows if r["instagram"])
    print(f"[out] {csv_path}")
    print(f"[out] {len(rows)} leads | {with_ig} with IG | {managed} managed-signal | {indep} explicitly independent")
    return csv_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--niche", default="", help="search keyword, e.g. fitness, alt, gym")
    ap.add_argument("--max", type=int, default=25, help="max profiles (cost ~$0.02 each)")
    ap.add_argument("--max-likes", type=int, default=1000, help="cap likes to target newer/smaller models")
    ap.add_argument("--search-mode", default="new")
    ap.add_argument("--other-socials", action="store_true", help="also scrape non-IG socials")
    ap.add_argument("--reprocess", default="", help="path to a *_raw.json to re-map without re-scraping (free)")
    args = ap.parse_args()

    # Free path: re-run normalization on cached raw JSON during iteration.
    if args.reprocess:
        items = json.loads(Path(args.reprocess).read_text())
        print(f"[reprocess] {len(items)} cached profiles from {args.reprocess}")
        write_outputs(normalize(items), None, args.niche or "reprocess")
        return

    token = load_token()
    run_input = {
        "searchMode": args.search_mode,
        "additionalKeywords": args.niche,
        "maxProfiles": args.max,
        "requireInstagram": True,
        "maxLikes": args.max_likes,
        "scrapeOtherSocials": args.other_socials,
    }

    print(f"[run] actor={ACTOR} niche='{args.niche or 'any'}' max={args.max} (~${args.max * 0.02:.2f})")
    run = api_call("POST", f"{API}/acts/{ACTOR}/runs", token, run_input)["data"]
    run_id = run["id"]
    print(f"[run] started id={run_id}, polling...")

    # Poll to completion.
    status = run["status"]
    waited = 0
    while status not in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
        time.sleep(10)
        waited += 10
        run = api_call("GET", f"{API}/actor-runs/{run_id}", token)["data"]
        status = run["status"]
        print(f"[run] {status} ({waited}s)")
        if waited > 1800:
            sys.exit("[run] timeout after 30 min")

    if status != "SUCCEEDED":
        sys.exit(f"[run] ended {status}")

    ds_id = run["defaultDatasetId"]
    items = api_call("GET", f"{API}/datasets/{ds_id}/items?clean=true&format=json", token)
    print(f"[data] {len(items)} profiles returned")
    if not items:
        sys.exit("[data] no items, try a different niche or searchMode")

    print(f"[data] sample field keys: {sorted(items[0].keys())}")
    write_outputs(normalize(items), items, args.niche)


if __name__ == "__main__":
    main()
