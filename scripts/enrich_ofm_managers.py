#!/usr/bin/env python3
"""
enrich_ofm_managers.py — Stage 2.5 of the OFM Manager Discovery pipeline.

Adds an outreach contact angle to each vetted agency: website, link-in-bio hub,
and Telegram. One logged-out Google SERP query per agency (ban-safe per the
Ban-Safety Doctrine, we never touch Instagram), parsing the agency's own
non-social properties out of the results.

Pipeline:
  1. Read leads/ofm_managers_master.csv (primary outreach targets by default).
  2. For each, SERP `<handle> onlyfans agency` and pull:
       telegram  -> first t.me/ link
       hub       -> first link-router (linktr.ee / beacons.ai / allmylinks)
       website   -> first real non-social domain
  3. Write leads/ofm_managers_master_enriched.csv with the contact fields filled.

Reuses the shared engine in find_ofm_managers.py. Logged-out SERP only, no IG.

Precision note: the website column is BEST-EFFORT (~75-80%). These keywords are
dominated by a few high-ranking agencies and the occasional big-brand collision
(e.g. a handle "verge" pulling theverge.com), which handle-to-domain matching
cannot fully disambiguate. The IG handle is the reliable Arm-B channel; treat the
website as a lead, eyeball before outreach. Telegram yield is near zero from this
query shape and is left for a dedicated pass.

Usage:
  python3 scripts/enrich_ofm_managers.py             # primaries only
  python3 scripts/enrich_ofm_managers.py --all       # every handle
"""

import argparse
import csv
import re
from pathlib import Path

from find_ofm_managers import load_env, run_apify_serp, log

REPO = Path(__file__).resolve().parents[1]
LEADS_DIR = REPO / "leads"
MASTER = LEADS_DIR / "ofm_managers_master.csv"

SOCIAL = (
    "instagram.com", "facebook.com", "fb.com", "fb.watch", "linkedin.com",
    "twitter.com", "x.com", "tiktok.com", "youtube.com", "youtu.be",
    "threads.net", "reddit.com", "pinterest.com", "snapchat.com",
)
ROUTERS = ("linktr.ee", "beacons.ai", "allmylinks.com", "linkin.bio", "hoo.be", "snipfeed.co", "tap.bio")
TG_RE = re.compile(r"(?:https?://)?(?:t\.me|telegram\.me)/([A-Za-z0-9_+]+)", re.I)
DOMAIN_RE = re.compile(r"https?://([^/]+)/?", re.I)


# generic words removed from a brand overlap; if nothing distinctive remains,
# the two only share boilerplate like "talentagency" and it is not a real match
GENERIC_TOKENS = [
    "agencies", "agency", "management", "manager", "mgmt", "mgt", "talents",
    "talent", "models", "model", "onlyfans", "ofm", "official", "creators",
    "creator", "media", "group", "studio", "global", "company", "the", "only", "of",
]


def _distinctive(s):
    for g in GENERIC_TOKENS:
        s = s.replace(g, "")
    return s


def _lcs(a, b):
    """Longest common substring of two short strings."""
    best = ""
    for i in range(len(a)):
        for j in range(i + len(best) + 1, len(a) + 1):
            if a[i:j] in b:
                best = a[i:j]
            else:
                break
    return best


def brand_match(handle, domain):
    """Accept a domain only if it shares a real brand stem with the handle.

    Kills the dominant false positive: the SERP for "<handle> onlyfans agency"
    is topped by the few agencies that rank for the keyword (astalentagency,
    tdmmanagement), and a naive match latches onto the shared generic words.
    The brand overlap must be a >=5-char run that is NOT itself a generic word.
    """
    h = re.sub(r"[^a-z0-9]", "", handle.lower())
    sld = domain.lower().split(".")
    sld = re.sub(r"[^a-z0-9]", "", sld[-2] if len(sld) >= 2 else sld[0])
    lcs = _lcs(h, sld)
    if len(lcs) < 5:
        return False
    # the overlap must carry a real brand stem, not just shared boilerplate
    return len(_distinctive(lcs)) >= 4


def classify_links(results, handle):
    telegram = hub = website = ""
    for r in results:
        url = r.get("url", "")
        if not url:
            continue
        mt = TG_RE.search(url)
        if mt and not telegram:
            telegram = f"t.me/{mt.group(1).lstrip('+')}"
            continue
        md = DOMAIN_RE.search(url)
        if not md:
            continue
        dom = md.group(1).lower().lstrip("www.")
        if any(s in dom for s in SOCIAL) or "onlyfans.com" in dom or "fansly" in dom:
            continue
        if any(rt in dom for rt in ROUTERS):
            if not hub and brand_match(handle, url.split("/")[3] if url.count("/") >= 3 else dom):
                hub = url.split("?")[0]
            continue
        if not website and brand_match(handle, dom):
            website = dom
    return telegram, hub, website


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="enrich every handle, not just primaries")
    args = ap.parse_args()
    load_env()

    if not MASTER.exists():
        log("master not found, run combine_leads.py first")
        return
    rows = list(csv.DictReader(MASTER.open(encoding="utf-8", errors="ignore")))
    targets = rows if args.all else [r for r in rows if r.get("is_primary") == "yes"]
    log(f"enriching {len(targets)} agencies via logged-out SERP")

    qmap, queries = {}, []
    for r in targets:
        q = f'{r["ig_handle"]} onlyfans agency'
        qmap[q] = r["ig_handle"]
        queries.append(q)

    # the run-sync endpoint is flaky on big/back-to-back calls, so batch + breathe
    import time
    BATCH = 15
    items = []
    for i in range(0, len(queries), BATCH):
        chunk = queries[i:i + BATCH]
        log(f"  batch {i // BATCH + 1} ({len(chunk)} queries)...")
        items.extend(run_apify_serp(chunk, results_per_page=8, max_pages=1) or [])
        time.sleep(2)

    # map each SERP item back to its handle by query term
    found = {}
    for item in items or []:
        sq = item.get("searchQuery", {})
        term = sq.get("term") if isinstance(sq, dict) else item.get("searchQuery", "")
        handle = qmap.get(term)
        if not handle:
            continue
        results = item.get("organicResults") or item.get("results") or []
        found[handle] = classify_links(results, handle)

    enriched = 0
    for r in rows:
        h = r.get("ig_handle")
        if h in found:
            tg, hub, web = found[h]
            r["telegram_handle"] = tg or r.get("telegram_handle", "")
            r["website"] = web or r.get("website", "")
            if hub and not r.get("website"):
                r["website"] = hub
            if tg or web or hub:
                enriched += 1

    out = LEADS_DIR / "ofm_managers_master_enriched.csv"
    cols = list(rows[0].keys())
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    log(f"enriched {enriched}/{len(targets)} agencies with a contact field -> {out}")
    print(str(out))


if __name__ == "__main__":
    main()
