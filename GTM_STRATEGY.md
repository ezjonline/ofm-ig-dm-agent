# OFM IG DM Agent — Go-To-Market + Deploy + Dashboard Strategy

EZJ asked the right questions on 2026-06-06:
1. How do we deploy to multiple OF creators?
2. Who do we sell to — OFMs or direct to creators?
3. What does the no-risk offer look like?
4. What's the attribution / dashboard story?

This doc captures the answers.

---

## 1. Who we sell to: OFMs, not creators

**Decision: sell to OnlyFans Management agencies. Not direct to creators.**

Why:

| | OFM agencies | Direct to creators |
|---|---|---|
| Decision maker | One operator, knows tools, has budget | Each creator individually |
| Sales cycle | ~7 days | ~30+ days |
| Per-deal ceiling | 5 to 30 creators per OFM | 1 creator |
| Sales-overhead-per-dollar | Low | 10x higher |
| Skepticism | Operators get it | Creators are skeptical of tools |
| Renewal risk | OFM eats the churn | Creator quits OF, gone |
| Existing buying behavior | OFMs already pay chatter teams $1.5k-3k/mo per creator | Most creators DIY their own DMs |
| Decision speed | Operator-fast | Creator-slow (consults boyfriend, friends, manager) |

A signed OFM at 5 creators = 5x the revenue and 1/5 the sales effort of 5 individually-signed creators.

**Tier-1 ICP (sell here first):**
- OFM with 5 to 30 creators
- Each creator $5k-$50k/mo on OF (mid-tier, room to grow)
- Each creator 5k-100k IG followers
- Operator (not the creator) makes the call
- Already paying for chatter teams (proves they invest in conversion ops)

**Tier-2 ICP (only after we have 3 OFM clients):** top-1% solo creators ($50k+/mo) who manage their own DMs and act like operators.

**Out of scope V1:** beginner creators (<$5k/mo, not enough volume to justify our build cost).

---

## 2. The deploy model: per-creator under one OFM master

**One n8n workflow per creator, one ManyChat app per creator, all under one OFM "tenant."**

Why per-creator (not per-OFM):
- Each creator has different voice, sub price, content pillars, hard NOs.
- ManyChat custom fields are per-IG-account anyway.
- A creator joining or leaving an OFM should be a one-command deploy/teardown, not a multi-creator rewire.
- Per-creator metrics let us bill performance share by creator.

The deploy script template:

```bash
# Onboard a new creator (90 minutes total)
python3 scripts/onboard_creator.py \
  --ofm-slug monetize-me \
  --creator-handle mia_alt \
  --creator-name "Mia" \
  --of-url https://onlyfans.com/miaalt \
  --sub-price 9.99 \
  --kb-doc-url https://docs.google.com/document/d/... \
  --manychat-token mc_xxxxx
```

What this script does (to build, not yet built):
1. Clones the production n8n workflow template, swaps in all `<CREATOR_HANDLE>` placeholders
2. Creates ManyChat custom fields via API (no UI clicking needed)
3. Creates the trigger flows via ManyChat API
4. Wires the Send Flow + webhook
5. Saves the creator config to our central tenant database
6. Returns a "go live" checklist for the human (creator review of 10 sample convos, etc.)

**This is the V2 build priority after Harvey pilot closes.** For V1 Harvey deploy we do it manually per the existing `manychat_setup_guide.md` (~90 min). Once we have 2 creators deployed manually, we know exactly what to automate.

---

## 3. The no-risk offer

**Sell it as: "We install for free. You pay us a percentage of new OF subs we close. Zero downside."**

This is the right pitch for OFMs because:
- They've never run an IG DM bot before; the unknown scares them
- Their existing chatter cost is variable; a fixed setup fee feels like a step backwards
- A revenue share aligns incentives: if Bella doesn't convert, OFM pays nothing
- OFMs already pay 30-50% rev share to their chatter teams; our 15% feels reasonable

**The offer (locked, awaiting Hormozi-pricing validation):**

| | Standard | Founder rate (Harvey + next 2 OFMs) |
|---|---|---|
| Setup fee | $0 (we eat the 90-min install per creator) | $0 |
| Performance share | 15% of net new OF sub revenue (rolling 30-day attribution) | 10% locked for life |
| Minimum term | 90 days | 90 days |
| Setup includes | ManyChat app, knowledge base doc build, prompt customization, first 7 days monitoring, dashboard access | Same + case study rights |
| Cancellation | 30 days notice after the 90-day minimum | Same |
| What's NOT included | The OFM's existing chatter team (we don't replace them, we feed them warm subs) | Same |

**Sales script TL;DR:** "We install for free, no setup fee, no monthly retainer. We take 15% of new OF subs we attribute to our IG DM bot. If we don't perform, you pay us nothing and walk away after 90 days. Worst case we cost you 90 days of a ManyChat seat ($15/mo). Best case we add 30-50% to your top line per creator."

OFMs say yes to this because there's literally no downside.

---

## 4. The attribution dashboard

**For V1: simple Retool dashboard reading from a SQLite log of every Bella tool call.**

The architecture:

```
ManyChat (or simulator chat.html)
    v
n8n OFM workflow
    +-- Bella fires apply_tag (e.g. Subscribed)
    |       |
    |       v
    |   Mock ManyChat (sim) OR real ManyChat (prod)
    |
    +-- AND parallel: writes to attribution log
            |
            v
        Supabase / Postgres table:
            attribution_events (
              creator_handle,
              session_id,
              tag,             -- OF_Link_Pitched, Subscribed, Disqualified, etc.
              fan_country,
              fan_age,
              vibe, interests,
              subbed_tier,
              event_at,
              ofm_id
            )
            v
        Retool / Next.js dashboard:
            - Per-OFM tenant login
            - Per-creator funnel (DMs received -> qualified -> OF_Link_Pitched -> Subscribed)
            - Cohort revenue attribution (subs subscribed via bot, rolling 30/60/90 day)
            - Bella conversation review (anonymized samples)
            - Billing: 15% of attributable sub revenue this month, auto-invoice
```

**What we build in what order:**

| Stage | What | When |
|-------|------|------|
| V1.0 today | Manual: n8n + ManyChat + mock-mc | DONE |
| V1.1 next | Add a parallel n8n branch that POSTs every tool call to a Supabase table | Day 3 of Harvey pilot |
| V1.2 | Retool dashboard wired to Supabase, internal-only | Day 7 of Harvey pilot |
| V1.3 | Per-OFM tenant view, invite Harvey to log in | Day 14 of Harvey pilot |
| V1.4 | Auto-invoice based on Subscribed tags + creator sub price | Day 30 (first billing cycle) |
| V2 | Cross-check ManyChat Subscribed tag against OF dashboard (reduces false positives) | Month 2 |
| V3 | Multi-tenant onboarding UI (an OFM can self-serve add a new creator) | Month 3+ |

**The point: dashboard is V1.1 not V1.0.** We need ONE live creator working before we build attribution infra. Otherwise we're building the meter before the water flows.

But you're 100% right that the dashboard is the GTM unlock. "Free install, you only pay for results, here's a live dashboard showing every sub we closed for you" is the close. Without the dashboard, the rev-share story is hand-wavy.

---

## 5. Demo readiness checklist

Goal: be demo-ready to pitch any OFM by 2026-06-13 (7 days).

| | Status |
|---|---|
| Bella's prompt tuned and stable | ⚠️ gpt-4o slips dashes occasionally, swap to Sonnet 4.6 when credits land |
| Chat.html as a live demo tool that runs Bella against Mia | ✅ DONE |
| Mia's persona feels real | ⚠️ EZJ to test, flag what's off |
| Loom: 90-second demo showing chat.html in action | ❓ Not recorded |
| One-pager PDF of the offer (setup fee $0, 15% rev share, 90-day min) | ❓ Not built |
| Attribution dashboard mockup (even if just a Figma) for the demo | ❓ Not built |
| Outreach DM template for OFMs | ❓ Not built |
| Hormozi-pricing run to validate the 15% number | ❓ Not run |

The 5 things to build before pitching the next OFM after Harvey:
1. Polish chat.html into a demo-able experience (already 80% there)
2. Record one Loom showing Bella in action
3. Build the offer one-pager
4. Mock the dashboard in Figma (so the rev-share story has a visual)
5. Draft 3 outreach DMs targeting OFMs we identify

I'd estimate 1 day of EZJ + Claudia time for all five.

---

## 6. The long-term vision (what you said matters for direction)

You mentioned a backend dashboard where OFMs can see the AI's attribution, and that it's the incentive that justifies the rev share. That's correct, and we should build toward that from day 1.

The vision in priority order:

```
NOW             Bella works. Single creator. Manual deploy. chat.html testing.
+1 week         Harvey pilot deploys. 1 real creator. Manual attribution log.
+2 weeks        Bella attribution table in Supabase. Internal Retool dashboard.
+1 month        First OFM-facing dashboard (Harvey logs in, sees his numbers).
+2 months       Multi-tenant. Auto-invoice. 3+ OFMs onboarded.
+3 months       Self-serve creator onboarding (an OFM operator clicks "add creator").
+6 months       Chrome extension V2: Bella's sister Maya runs the on-platform chats too.
+12 months      We've replaced or augmented chatter teams across 20+ OFMs.
```

The $10k MRR goal is hit somewhere between month 2 and month 3 if we close 2-3 OFMs at 5 creators each on the 15% rev share.

The product economics: a mid-tier creator at $20k/mo on OF, gets 20% lift from Bella = $4k/mo new sub revenue, our cut = $600/mo. Five creators per OFM = $3k MRR per OFM. Three OFMs and we've hit $10k.

**That's the actual path. Everything we build between now and there serves that math.**

---

## 7. What's blocking us from selling THIS WEEK

Three things. None are big:

1. **Harvey's nod on a pilot creator.** Ping him today.
2. **Anthropic credits topped up** (or fresh API key) so we can swap Bella from gpt-4o to Sonnet 4.6 for better rule adherence.
3. **A 90-second demo Loom** showing Bella converting a fake fan through chat.html.

That's it. Once those three land, we can start pitching cold outbound to other OFMs in parallel with the Harvey pilot. We don't need the dashboard to make the first sale; we need the dashboard by day 14 of the first deployment so the OFM stays bought in.
