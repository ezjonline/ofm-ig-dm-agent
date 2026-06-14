#!/usr/bin/env python3
"""
bridge_ofm_managers.py — Stage 2 of the OFM Manager Discovery pipeline.

The name-to-IG bridge. Stage 1 (find_ofm_managers.py) only catches agencies whose
Instagram bio is literally titled "OnlyFans Management". Stage 2 reaches the
professionalized agencies that are listed on LinkedIn but do not bio-title that
way: it sources agency NAMES from LinkedIn company SERPs, then bridges each name
to its Instagram handle with a second SERP pass, scored and Haiku-judged exactly
like Stage 1.

Pipeline:
  1. SERP source: `site:linkedin.com/company "OnlyFans Management Agency"` etc.
     -> extract the agency name from the LinkedIn result title.
  2. Bridge: for each name, `site:instagram.com "<name>"` -> extract @handle.
  3. Score + mandatory Haiku judge gate (operator | model | collision | unsure).
  4. De-dupe against everything already in leads/, write a scored CSV with the
     sourcing LinkedIn URL carried through for enrichment.

Reuses the shared engine in find_ofm_managers.py.

Source playbook: GTM_OFM_MANAGER_DISCOVERY.md (vectors: linkedin-to-ig, name bridge)

Usage:
  python3 scripts/bridge_ofm_managers.py
  python3 scripts/bridge_ofm_managers.py --no-judge
"""

import argparse
import csv
import re
import sys
import time
from datetime import datetime, timezone

from find_ofm_managers import (
    load_env, run_apify_serp, parse_serp, anthropic_judge,
    load_known_handles, LEADS_DIR, log,
)


def linkedin_name_queries():
    return [
        'site:linkedin.com/company "OnlyFans Management Agency"',
        'site:linkedin.com/company "OnlyFans management"',
        'site:linkedin.com/company "OF management agency"',
        'site:linkedin.com/company "creator management" OnlyFans',
        'site:linkedin.com/company "OnlyFans agency"',
    ]


def extract_agency_names(items):
    """LinkedIn company SERP titles -> clean agency names + the LinkedIn URL."""
    names = {}
    for item in items or []:
        for r in item.get("organicResults") or item.get("results") or []:
            url = r.get("url", "")
            if "linkedin.com/company" not in url:
                continue
            title = r.get("title", "")
            # "Agency Name | LinkedIn" or "Agency Name - tagline | LinkedIn"
            name = re.split(r"\s*\|\s*linkedin", title, flags=re.I)[0]
            name = re.split(r"\s+[-|]\s+", name)[0].strip()
            key = name.lower()
            if name and len(name) > 2 and "linkedin" not in key and key not in names:
                names[key] = {"name": name, "linkedin_url": url}
    return list(names.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-pages", type=int, default=2, help="LinkedIn SERP pages per sourcing query")
    ap.add_argument("--min-score", type=int, default=1, help="bridge name-match is itself a signal, so lower default")
    ap.add_argument("--no-judge", action="store_true")
    ap.add_argument("--keep-unsure", action="store_true")
    args = ap.parse_args()

    load_env()

    # 1. source agency names from LinkedIn
    src_items = run_apify_serp(linkedin_name_queries(), results_per_page=20, max_pages=args.source_pages)
    agencies = extract_agency_names(src_items)
    log(f"sourced {len(agencies)} agency names from LinkedIn")
    if not agencies:
        log("no agency names sourced, nothing to bridge")
        return

    # 2. bridge each name to its IG handle, tracking which query came from which agency
    qmap = {}
    queries = []
    for a in agencies:
        q = f'site:instagram.com "{a["name"]}"'
        qmap[q] = a
        queries.append(q)
    bridge_items = run_apify_serp(queries, results_per_page=10, max_pages=1)
    cands = parse_serp(bridge_items)
    log(f"bridged to {len(cands)} unique IG candidates")

    # attach the sourcing agency (by source_query) for enrichment
    for c in cands:
        a = qmap.get(c.get("source_query"))
        c["linkedin_url"] = a["linkedin_url"] if a else ""
        c["operator_name"] = ""

    scored = [c for c in cands if c["score"] >= args.min_score]
    known = load_known_handles()
    scored = [c for c in scored if c["ig_handle"] not in known]
    log(f"{len(scored)} candidates scored >= {args.min_score} and new vs existing leads/")

    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if args.no_judge or not api_key:
        for c in scored:
            c["judge_verdict"] = "skipped"
        kept = scored
    else:
        log(f"judging {len(scored)} bridged candidates...")
        for c in scored:
            c["judge_verdict"] = anthropic_judge(c, api_key)
            time.sleep(0.15)
        allow = {"operator"} | ({"unsure"} if args.keep_unsure else set())
        kept = [c for c in scored if c["judge_verdict"] in allow]
    log(f"{len(kept)} operators kept after judge gate")

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    LEADS_DIR.mkdir(exist_ok=True)
    out_path = LEADS_DIR / f"ofm_managers_bridge_{ts}.csv"
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
                "operator_name": c.get("operator_name", ""),
                "linkedin_url": c.get("linkedin_url", ""),
                "website": "",
                "telegram_handle": "",
                "source_vector": "linkedin-name-bridge",
                "source_url": c["source_url"],
                "source_query": c["source_query"],
                "score": c["score"],
                "score_reasons": c["score_reasons"],
                "follower_count_est": "",
                "judge_verdict": c["judge_verdict"],
            })
    log(f"wrote {len(kept)} bridged operator leads -> {out_path}")
    print(str(out_path))


if __name__ == "__main__":
    main()
