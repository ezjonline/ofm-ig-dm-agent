#!/usr/bin/env python3
"""
combine_leads.py — merge every OFM operator lead CSV into one outreach-ready master.

Stage 1 (find_ofm_managers) and Stage 2 (bridge_ofm_managers) each write their own
timestamped CSV, and the same agency often appears under several handle variants
(@thesirenagency, @sirenagency___, @joinsiren all = "Siren Agency"). This pass:

  1. Loads every leads/ofm_managers_*.csv.
  2. De-dupes exact handles (keeps the highest score / a real judge verdict).
  3. Clusters near-duplicate handles by a normalized agency name, so outreach hits
     each agency once instead of spamming the same operator four times.
  4. Flags one primary handle per cluster (highest score = best outreach target).
  5. Writes leads/ofm_managers_master.csv, sorted, with cluster_id + is_primary.

Usage: python3 scripts/combine_leads.py
"""

import csv
import glob
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEADS_DIR = REPO / "leads"

# generic agency words stripped before clustering, so the brand core is what matches
STOP = {
    "agency", "agencies", "management", "mgmt", "mgt", "ofm", "onlyfans", "of",
    "the", "models", "model", "talent", "official", "promo", "media", "group",
    "co", "llc", "inc", "photo", "by", "and", "x",
}


def cluster_key(name, handle):
    toks = re.findall(r"[a-z0-9]+", (name or "").lower())
    core = [t for t in toks if t not in STOP]
    key = "".join(sorted(core))
    if not key:  # name was all generic words, fall back to the handle stem
        key = re.sub(r"[^a-z0-9]", "", (handle or "").lower())
    return key


def main():
    files = sorted(glob.glob(str(LEADS_DIR / "ofm_managers_*.csv")))
    files = [f for f in files if "master" not in f]
    if not files:
        print("no lead CSVs found")
        return

    by_handle = {}
    for fn in files:
        with open(fn, newline="", encoding="utf-8", errors="ignore") as f:
            for r in csv.DictReader(f):
                h = (r.get("ig_handle") or "").strip().lower()
                if not h:
                    continue
                try:
                    r["_score"] = int(r.get("score") or 0)
                except ValueError:
                    r["_score"] = 0
                prev = by_handle.get(h)
                # keep the richer record: higher score, prefer a real verdict over skipped
                if prev:
                    better = r["_score"] > prev["_score"] or (
                        prev.get("judge_verdict") == "skipped" and r.get("judge_verdict") != "skipped"
                    )
                    if not better:
                        continue
                by_handle[h] = r

    rows = list(by_handle.values())

    # assign cluster ids
    clusters = {}
    for r in rows:
        k = cluster_key(r.get("agency_name", ""), r.get("ig_handle", ""))
        clusters.setdefault(k, []).append(r)

    cid_for = {}
    for i, k in enumerate(sorted(clusters), start=1):
        cid_for[k] = i

    # flag the highest-score handle in each cluster as primary outreach target
    for k, members in clusters.items():
        members.sort(key=lambda x: -x["_score"])
        for j, r in enumerate(members):
            r["_cluster_id"] = cid_for[k]
            r["_is_primary"] = "yes" if j == 0 else "no"

    out = LEADS_DIR / "ofm_managers_master.csv"
    cols = [
        "cluster_id", "is_primary", "agency_name", "ig_handle", "yields_target",
        "operator_name", "linkedin_url", "website", "telegram_handle",
        "source_vector", "source_url", "score", "score_reasons",
        "follower_count_est", "judge_verdict",
    ]
    rows.sort(key=lambda x: (x["_cluster_id"], -x["_score"]))
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({
                "cluster_id": r["_cluster_id"],
                "is_primary": r["_is_primary"],
                "agency_name": r.get("agency_name", ""),
                "ig_handle": r.get("ig_handle", ""),
                "yields_target": r.get("yields_target", "brand"),
                "operator_name": r.get("operator_name", ""),
                "linkedin_url": r.get("linkedin_url", ""),
                "website": r.get("website", ""),
                "telegram_handle": r.get("telegram_handle", ""),
                "source_vector": r.get("source_vector", ""),
                "source_url": r.get("source_url", ""),
                "score": r.get("score", ""),
                "score_reasons": r.get("score_reasons", ""),
                "follower_count_est": r.get("follower_count_est", ""),
                "judge_verdict": r.get("judge_verdict", ""),
            })

    n_clusters = len(clusters)
    n_primary = sum(1 for r in rows if r["_is_primary"] == "yes")
    print(f"merged {len(files)} files -> {len(rows)} unique handles across "
          f"{n_clusters} agency clusters ({n_primary} primary outreach targets)")
    print(str(out))


if __name__ == "__main__":
    main()
