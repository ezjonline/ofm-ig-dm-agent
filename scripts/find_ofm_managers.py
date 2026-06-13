#!/usr/bin/env python3
"""
find_ofm_managers.py — Stage 1 of the OFM Manager Discovery pipeline.

Pulls OnlyFans management agency / operator Instagram handles straight out of the
Google SERP, with no IG login and no profile scrape, then scores and LLM-judges
each candidate so only real operators (not creators, not name collisions) ship.

Why this works: Google indexes every IG page title as
    "Display Name (@handle) Instagram photos and videos"
so a `site:instagram.com` search plus one regex extracts the handle from the
result title. Fully automatable, solid, zero ban risk on our side (we read
Google's SERP, we never touch Instagram directly here).

Pipeline:
  1. Build a query matrix (anchor x site filter x recruiting-CTA token).
  2. Run Apify `apify/google-search-scraper` over the matrix.
  3. Extract @handle from each instagram.com result (URL first, title fallback).
  4. Score: +1 mgmt keyword in display name, +1 handle-suffix convention,
     +1 recruiting CTA token in the snippet. Keep score >= 2.
  5. LLM-judge gate (Haiku): operator | model | collision | unsure. Keep operators.
     This gate is load-bearing: the name->IG bridge is collision-prone.
  6. De-dupe against existing leads/ and prior runs, write a scored CSV.

Source playbook: GTM_OFM_MANAGER_DISCOVERY.md

Usage:
  python3 scripts/find_ofm_managers.py                 # full run
  python3 scripts/find_ofm_managers.py --no-judge      # skip LLM gate (cheaper, noisier)
  python3 scripts/find_ofm_managers.py --max-pages 2   # deeper SERP crawl per query
"""

import argparse
import csv
import json
import os
import re
import ssl
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CTX = ssl.create_default_context()

REPO = Path(__file__).resolve().parents[1]
LEADS_DIR = REPO / "leads"
SECRETS_ENV = Path.home() / ".claude-secrets" / "claudia" / ".env"
LOCAL_ENV = REPO / ".env"

APIFY_ACTOR = "apify~google-search-scraper"
JUDGE_MODEL = "claude-haiku-4-5-20251001"

# ---- detection signals (from GTM_OFM_MANAGER_DISCOVERY.md) -------------------

MGMT_KEYWORDS = [
    "management", "mgmt", "agency", "talent", "creator management",
    "ofm", "model management", "talent management",
]
# convention suffixes operators put on the handle itself
HANDLE_SUFFIX_RE = re.compile(
    r"(\.agency|\.mgmt|\.ofm|_ofm|_mgmt|management|agencyy?_?|models?)$", re.I
)
# recruiting funnel + status proof tokens that show up in the SERP snippet
CTA_TOKENS = [
    "apply below", "apply to work", "dm to apply", "now signing", "now accepting",
    "accepting applications", "apply via link", "dm for management", "dm for collab",
    "dm for promo", "top 1%", "top 0.01%", "promote, manage", "scale your",
    "creator revenue", "in creator revenue", "trusted by",
]
# negative signals: this is a creator/model, not an operator
NEGATIVE_TOKENS = ["no agencies", "no agency", "onlyfans.com/", "fansly.com/"]

# IG URL paths that are not profiles
NON_PROFILE_PATHS = {"p", "reel", "reels", "explore", "stories", "tv", "s", "directory", "accounts"}

HANDLE_IN_TITLE_RE = re.compile(r"\(@([A-Za-z0-9._]+)\)")
HANDLE_IN_URL_RE = re.compile(r"instagram\.com/([A-Za-z0-9._]+)/?", re.I)


def log(msg):
    print(f"[find_ofm_managers] {msg}", file=sys.stderr, flush=True)


def load_env():
    """Load KEY=VALUE pairs from the secrets .env, tolerating malformed lines."""
    for envf in (LOCAL_ENV, SECRETS_ENV):
        if not envf.exists():
            continue
        for line in envf.read_text(errors="ignore").splitlines():
            m = re.match(r"^([A-Z][A-Z0-9_]*)=(.*)$", line)
            if m and m.group(1) not in os.environ:
                os.environ[m.group(1)] = m.group(2).strip().strip('"').strip("'")


def build_queries(niches=None):
    """Query matrix: agency anchors x recruiting-CTA tokens, scoped to IG.

    Optionally niche-qualified (e.g. fitness, alt, cosplay) to reach agencies
    that brand around a vertical instead of the generic "management" wording.
    """
    site = "site:instagram.com"
    anchors = [
        '"OnlyFans management agency"',
        '"OnlyFans management"',
        '"OF management agency"',
        '"OFM agency"',
        '"creator management" OnlyFans',
        '"we manage OnlyFans"',
        '"model management" OnlyFans',
        '"talent agency" OnlyFans',
        '"adult content agency" management',
        '"OnlyFans agency"',
    ]
    cta = [
        '"now signing"', '"DM to apply"', '"apply below"', '"top 1%"',
        '"now accepting" models', '"scale your OnlyFans"',
    ]
    queries = []
    for a in anchors:
        queries.append(f"{site} {a}")
    # cross the strongest anchors with CTA/proof tokens for higher-intent pages
    for a in ('"OnlyFans management"', '"OFM agency"', '"OnlyFans agency"'):
        for c in cta:
            queries.append(f"{site} {a} {c}")
    # niche-qualified variants (agencies that brand around a vertical)
    for n in (niches or []):
        queries.append(f'{site} "{n}" "OnlyFans management agency"')
        queries.append(f'{site} "{n}" "OnlyFans agency" signing')
    # the confirmed seed query (caps mimics how operators title their bios)
    queries.append("ONLYFANS MANAGEMENT AGENCY instagram")
    # de-dupe, preserve order
    seen, out = set(), []
    for q in queries:
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out


def run_apify_serp(queries, results_per_page, max_pages, timeout=240):
    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        log("ERROR: APIFY_API_TOKEN not set")
        sys.exit(1)
    payload = {
        "queries": "\n".join(queries),
        "resultsPerPage": results_per_page,
        "maxPagesPerQuery": max_pages,
        "countryCode": "us",
        "languageCode": "en",
        "mobileResults": False,
        "saveHtml": False,
        "includeUnfilteredResults": False,
    }
    url = (
        f"https://api.apify.com/v2/acts/{APIFY_ACTOR}"
        f"/run-sync-get-dataset-items?token={token}"
    )
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    log(f"running Apify SERP over {len(queries)} queries (resultsPerPage={results_per_page}, maxPages={max_pages})...")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        log(f"Apify HTTP {e.code}: {e.read().decode()[:300]}")
        sys.exit(1)
    except Exception as e:
        log(f"Apify call failed: {e}")
        sys.exit(1)


def extract_handle(url, title):
    h = None
    mu = HANDLE_IN_URL_RE.search(url or "")
    if mu:
        cand = mu.group(1)
        if cand.lower() not in NON_PROFILE_PATHS:
            h = cand
    if not h:
        mt = HANDLE_IN_TITLE_RE.search(title or "")
        if mt:
            h = mt.group(1)
    if not h:
        return None
    return h.strip(".").lower()


def display_name(title):
    # "Lush MGMT (@thelushmgmt) • Instagram photos and videos" -> "Lush MGMT"
    return re.split(r"\(@", title or "", maxsplit=1)[0].strip()


def score_candidate(title, handle, snippet):
    name = display_name(title).lower()
    snip = (snippet or "").lower()
    score, reasons = 0, []
    if any(k in name for k in MGMT_KEYWORDS):
        score += 1
        reasons.append("mgmt-keyword-in-name")
    if HANDLE_SUFFIX_RE.search(handle):
        score += 1
        reasons.append("handle-suffix-convention")
    if any(t in snip for t in CTA_TOKENS):
        score += 1
        reasons.append("recruiting-cta-in-snippet")
    return score, reasons


def parse_serp(items):
    """Flatten Apify SERP items -> instagram profile candidates."""
    cands = {}
    for item in items or []:
        organics = item.get("organicResults") or item.get("results") or []
        sq = item.get("searchQuery", {})
        query = sq.get("term") if isinstance(sq, dict) else item.get("searchQuery", "")
        for r in organics:
            url = r.get("url", "")
            if "instagram.com" not in url:
                continue
            title = r.get("title", "")
            snippet = r.get("description", "") or r.get("snippet", "")
            handle = extract_handle(url, title)
            if not handle:
                continue
            score, reasons = score_candidate(title, handle, snippet)
            prev = cands.get(handle)
            if prev and prev["score"] >= score:
                continue
            cands[handle] = {
                "ig_handle": handle,
                "agency_name": display_name(title),
                "title": title,
                "snippet": snippet[:400],
                "source_url": f"https://www.instagram.com/{handle}/",
                "source_query": query,
                "score": score,
                "score_reasons": ";".join(reasons),
            }
    return list(cands.values())


def anthropic_judge(cand, api_key, timeout=40):
    """One Haiku call -> operator | model | collision | unsure."""
    prompt = (
        "You are vetting an Instagram account for a B2B lead list of OnlyFans "
        "MANAGEMENT AGENCIES / operators (businesses that recruit, manage, chat for, "
        "and scale OF creators).\n\n"
        f"Display name: {cand['agency_name']}\n"
        f"Handle: @{cand['ig_handle']}\n"
        f"SERP snippet: {cand['snippet']}\n\n"
        "Classify this account as exactly one word:\n"
        "operator  = an agency that specifically recruits/manages/scales OnlyFans (adult/18+) creators\n"
        "model     = an individual creator's own page (a product, not a buyer)\n"
        "collision = a GENERIC talent, influencer, modeling, marketing, or digital agency that is\n"
        "            NOT specifically OnlyFans/adult focused, OR any unrelated business sharing a name\n"
        "unsure    = not enough signal\n\n"
        "Only answer 'operator' if there is OnlyFans / adult-creator / fansly / PPV / subs / 18+ "
        "evidence. A mainstream talent or marketing agency with no adult signal is 'collision'.\n"
        "Answer with only the one word."
    )
    body = json.dumps({
        "model": JUDGE_MODEL,
        "max_tokens": 5,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
            out = json.loads(r.read().decode())
        txt = "".join(b.get("text", "") for b in out.get("content", [])).strip().lower()
        for v in ("operator", "model", "collision", "unsure"):
            if v in txt:
                return v
        return "unsure"
    except Exception as e:
        log(f"judge failed for @{cand['ig_handle']}: {e}")
        return "unsure"


def load_known_handles():
    """De-dupe set: every handle already in leads/ CSVs (creators + prior runs)."""
    known = set()
    if not LEADS_DIR.exists():
        return known
    for csvf in LEADS_DIR.glob("*.csv"):
        try:
            with csvf.open(newline="", encoding="utf-8", errors="ignore") as f:
                for row in csv.DictReader(f):
                    for col in ("ig_handle", "instagram", "ig_username"):
                        v = (row.get(col) or "").strip().lower()
                        v = re.sub(r"^@|/$", "", v.replace("https://www.instagram.com/", ""))
                        if v:
                            known.add(v)
        except Exception:
            continue
    return known


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-per-page", type=int, default=30)
    ap.add_argument("--max-pages", type=int, default=1)
    ap.add_argument("--min-score", type=int, default=2)
    ap.add_argument("--no-judge", action="store_true", help="skip the LLM-judge gate")
    ap.add_argument("--keep-unsure", action="store_true", help="also keep 'unsure' verdicts")
    ap.add_argument("--niches", default="", help="comma-separated niches to qualify queries, e.g. fitness,alt,cosplay")
    args = ap.parse_args()

    load_env()
    niches = [n.strip() for n in args.niches.split(",") if n.strip()]
    queries = build_queries(niches)
    items = run_apify_serp(queries, args.results_per_page, args.max_pages)
    cands = parse_serp(items)
    log(f"parsed {len(cands)} unique IG candidates from SERP")

    scored = [c for c in cands if c["score"] >= args.min_score]
    log(f"{len(scored)} candidates scored >= {args.min_score}")

    known = load_known_handles()
    scored = [c for c in scored if c["ig_handle"] not in known]
    log(f"{len(scored)} after de-dupe against existing leads/")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if args.no_judge or not api_key:
        if not api_key and not args.no_judge:
            log("WARNING: ANTHROPIC_API_KEY missing, skipping judge gate")
        for c in scored:
            c["judge_verdict"] = "skipped"
        kept = scored
    else:
        log(f"judging {len(scored)} candidates with {JUDGE_MODEL}...")
        for c in scored:
            c["judge_verdict"] = anthropic_judge(c, api_key)
            time.sleep(0.15)
        allow = {"operator"} | ({"unsure"} if args.keep_unsure else set())
        kept = [c for c in scored if c["judge_verdict"] in allow]
    log(f"{len(kept)} operators kept after judge gate")

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    LEADS_DIR.mkdir(exist_ok=True)
    out_path = LEADS_DIR / f"ofm_managers_{ts}.csv"
    cols = [
        "agency_name", "ig_handle", "yields_target", "operator_name", "linkedin_url",
        "website", "telegram_handle", "source_vector", "source_url", "source_query",
        "score", "score_reasons", "follower_count_est", "judge_verdict",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for c in sorted(kept, key=lambda x: -x["score"]):
            w.writerow({
                "agency_name": c["agency_name"],
                "ig_handle": c["ig_handle"],
                "yields_target": "brand",
                "operator_name": "",
                "linkedin_url": "",
                "website": "",
                "telegram_handle": "",
                "source_vector": "bio-handle-serp",
                "source_url": c["source_url"],
                "source_query": c["source_query"],
                "score": c["score"],
                "score_reasons": c["score_reasons"],
                "follower_count_est": "",
                "judge_verdict": c["judge_verdict"],
            })
    log(f"wrote {len(kept)} operator leads -> {out_path}")
    print(str(out_path))


if __name__ == "__main__":
    main()
