# Attribution: How We Prove Bella Drove The Sub

Foundation for the rev-share model. Without solid attribution, the pitch to OFMs ("you owe us 15% of $X") collapses. With it, the pitch is a screenshot.

This doc captures the actual stack we're building and what's possible vs not.

---

## The hard truth first

**OnlyFans has no public API.** No way to query "who subbed and where did they come from." This is not a "build it later" problem; it's a permanent constraint we have to engineer around.

What OF DOES give us:
- **Promo campaigns** — creators can set up trackable promo URLs (custom trial pricing/duration). The OF dashboard then shows per-promo: subs, revenue, churn. This is the closest thing to attribution OF provides.
- **The creator's dashboard** — a creator (or OFM) sees their own subscriber list with sub date and which promo (if any) they came in through.

What OF DOES NOT give us:
- Per-fan source (IG vs Twitter vs Reddit)
- UTM passthrough (if you put `?utm_source=ig_bot` on an OF link, it disappears at signup)
- API access to subscriber data

So our attribution stack has to combine OF's promo system with our own tracking. Four layers.

---

## The four-layer attribution stack

### Layer 1: Bot funnel events (Supabase, source-of-truth for funnel)

Every event Bella fires gets logged to a Supabase table. This is V1.1 build — we're not yet logging here, only firing to ManyChat custom fields.

```
ALTER TABLE attribution_events (
  id              uuid primary key,
  creator_handle  text,              -- 'mia_everyday'
  ofm_id          text,              -- 'monetize_me'
  session_id      text,              -- ManyChat subscriber id (uniquely tracks a fan)
  event_type      text,              -- conversation_started, qualified, link_pitched,
                                     -- link_clicked, sub_reported, disqualified
  phase           int,               -- 0..5 from Bella's flow
  payload         jsonb,             -- full event data
  event_at        timestamptz default now()
);
```

What we capture:
| Event | When fired | Source |
|---|---|---|
| `conversation_started` | First inbound DM hits webhook | n8n adds a Supabase row alongside the existing flow |
| `qualified` | Bella fires `save_qualification_data` with qualified=true | Tool call payload mirrored to Supabase |
| `discovered` | Bella fires `save_discovery_data` | Tool call payload mirrored |
| `link_pitched` | Bella fires `apply_tag OF_Link_Pitched` | Tag fire mirrored |
| `link_clicked` | Fan clicks the OF link | See Layer 2 |
| `sub_reported` | Fan tells Bella "I subbed" → fires `save_subscription_data` | Tool call payload mirrored |
| `sub_confirmed` | Cross-referenced with OF promo dashboard (Layer 3) | Manual or scraped |
| `disqualified` | Under 18 / hostile / fired Disqualified_Lead tag | Tag fire mirrored |

Why this matters: the funnel metrics OFMs care about (conversations → qualified → pitched → clicked → subbed) live here. The bot side is our ground truth for everything except the actual sub. Sub confirmation is Layer 3.

### Layer 2: Tracked short link (our domain, our click data)

Bella never drops the bare OF URL. She drops a short link on our domain that 302-redirects to the OF promo URL.

```
DM: "I'll drop the link if you wanna check it out: m.iaeveryday.com/sub"
                                                    ↓
                                              [our redirector]
                                                    ↓
                                                  logs:
                                                    session_id (from URL hash)
                                                    clicked_at
                                                    ip / user-agent
                                                    creator_handle
                                                    ofm_id
                                                    ↓
                                            302 redirect to:
                                            onlyfans.com/action/trial/bot-mia-001
```

Implementation: Cloudflare Workers + a $12/yr domain per creator OR one shared domain with per-creator path (`m.bellaroutes.com/mia/sub?s=<session>`).

Each click writes a `link_clicked` event to Supabase. This is the second strongest attribution signal (the first is Layer 3).

The short link also gives us:
- Cleaner-looking URL in the DM (looks less like an affiliate funnel)
- Easy to swap the destination URL without re-prompting Bella (creator changes her OF promo URL → we update the redirector, Bella keeps sending the same link)
- A/B testing different promo offers without prompt changes

### Layer 3: OF promo campaign (the billing source of truth)

Per creator, the OFM sets up a dedicated OF promo campaign for "IG bot driven" subs. OF gives them a unique promo URL.

```
OF dashboard > Promotions > New promo
  Name: "IG Bot Driven Subs"
  Discount: 50% off first month (matches what Bella offers)
  Expires: never (or quarterly rotation)
  URL: https://onlyfans.com/action/trial/abc123
```

That promo URL is what our redirector points to. When a fan clicks our short link, they get redirected to this promo URL, sub through it, and OF tags the sub with the promo name.

At end of month, the creator/OFM screenshots the promo report from their OF dashboard:
- "IG Bot Driven Subs" promo: 23 new subs this month, $342 gross revenue
- Our 15% = $51.30 owed

That screenshot is the billing source of truth. The OFM cuts us a check (or we auto-invoice).

**This is the only attribution OF actually supports.** Everything else (Layers 1, 2, 4) is corroborating evidence.

### Layer 4: Cross-reference for confidence

For each `sub_confirmed` event from OF dashboard, we cross-reference against Layer 1 + Layer 2:

- Was there a `link_clicked` event for the same creator within 72 hours before the sub?
- Was there a `link_pitched` event 5-60 minutes before the click?
- Did Bella's `save_subscription_data` fire (fan self-reported)?

Three-of-three = high confidence (bot definitely drove it).
Two-of-three = strong confidence.
One-of-three = weak (could be coincidence, fan found the link elsewhere).

This isn't billed differently — the OF promo number is what we bill — but the confidence score lets us defend against an OFM disputing that we drove a particular sub.

---

## What the OFM-facing dashboard looks like

V1.1 first cut (Retool MVP, ~1 day to build):

```
+--------------------------------------------------+
| Mia Everyday Sub Funnel (last 30d)               |
+--------------------------------------------------+
| Conversations started:                       342 |
| ├─ Qualified (age 18+, Tier 1):              218 |
| │  ├─ OF link pitched:                       147 |
| │  │  ├─ Link clicked:                        61 |
| │  │  │  └─ Subscribed (OF promo confirmed):  23 |
| │  │  └─ Pitched but didn't click:            86 |
| │  └─ Qualified but not pitched:              71 |
| └─ Disqualified:                             124 |
+--------------------------------------------------+
| Conversion rates                                 |
| Conv -> Qual: 64%   Qual -> Pitch: 67%           |
| Pitch -> Click: 41%   Click -> Sub: 38%          |
| End-to-end: 6.7%                                 |
+--------------------------------------------------+
| Revenue (this billing period)                    |
| Gross OF subs from bot: $342                     |
| Our 15% share owed: $51.30                       |
| Next invoice: 2026-07-01                         |
+--------------------------------------------------+
| Recent conversations (anonymized)                |
| [view 10 sample chats with PII redacted]         |
+--------------------------------------------------+
```

OFM logs in via per-tenant URL (e.g. `dashboard.bellaroutes.com/monetize-me`), sees their numbers, knows what they owe us. Settles via Stripe / Wise on the 1st of the month.

Internal dashboard adds: cost basis per conversation (LLM tokens, ManyChat, n8n cost), per-creator P&L, cohort churn at 30/60/90 days.

---

## Build sequence (V1.1 → V1.5)

| Version | What ships | When | Effort |
|---|---|---|---|
| V1.0 | Bella works, no formal attribution | DONE (today) | — |
| V1.1 | Supabase events table + n8n branches that log every tool call | Day 3 of Harvey pilot | 1 day |
| V1.2 | Custom short-link redirector (Cloudflare Workers) + click logging | Day 5 of Harvey pilot | 1 day |
| V1.3 | OF promo campaign per creator + manual monthly cross-reference | Day 7 of Harvey pilot | 30 min per creator (manual) |
| V1.4 | Retool dashboard wired to Supabase, OFM-facing per-tenant view | Day 14 | 1 day |
| V1.5 | Auto-invoice via Stripe based on OF promo subs cross-checked with Layer 1 | Day 30 | 1 day |

Total: 4-5 days of build over the first 30 days of Harvey's deploy. Front-loaded so attribution is rock-solid before the first billing cycle.

---

## What we can prove vs what we can't

**Can prove:**
- Fan came in through Bella's IG DMs
- Bella qualified them
- Bella pitched the link
- Fan clicked the link (our redirector logs)
- A sub appeared in the OF promo campaign within 72 hours

**Cannot prove (without OFM cooperation):**
- That this specific fan is the one who subbed in the OF dashboard
- Whether the fan saw the link elsewhere first (Twitter, IG bio, friend recommendation)

The defense: Layer 3 (OF promo subs) is the billing source. We're not billing per individual fan; we're billing per OF promo sub count. The 4-layer cross-reference is for the cases where an OFM disputes the bot drove the sub.

---

## What we need from each OFM at onboarding

For the attribution to work, each new creator deploy needs:
1. **OF promo campaign created** (5 min, OFM does this in their OF dashboard)
2. **OF promo URL shared with us** (we paste it into our redirector)
3. **Custom short-link domain or path assigned** (we create on Cloudflare)
4. **Bella's prompt updated** to use this creator's short link (auto via the knowledge base doc)
5. **OFM logs into our dashboard** (we create their tenant in V1.4)

Each onboarding step is 5-15 minutes. Per-creator setup is still ~90 min total (most of that is ManyChat). Attribution adds maybe 30 min on top.

---

## The pitch upgrade

Before attribution: "We install Bella for free, we get 15% of new subs she drives. Trust us, you'll see them in your dashboard."

After attribution (V1.4 ready): "Here's the dashboard. You see exactly which subs came through Bella, when they signed up, what they paid. We bill the 15% based on that promo campaign's reported revenue. If the OF promo says zero, we owe nothing. If it says $5k, we get $750. Zero argument."

The dashboard alone closes deals OFMs would otherwise hesitate on. It's not just attribution — it's trust theater that justifies the rev share.

---

## Phase 2 (AI creator) attribution

For Phase 2 we own everything, so attribution is trivial. We don't bill ourselves. The same Supabase + short link + OF promo stack just becomes our internal P&L dashboard. Same code, simpler use case.

---

## What we need to lock now

1. **Domain for the short link.** I recommend `bellaroutes.com` (one shared domain, per-creator paths) or `<creator-handle>.link` per creator. Shared is cheaper and faster. EZJ decides.
2. **Supabase project.** We probably need a dedicated Supabase project for this (not piggybacking on claudia's existing infra). Free tier covers V1.1-V1.4. EZJ creates it.
3. **Cloudflare account + Workers plan.** $5/mo for the redirector + click logging. EZJ already has Cloudflare.
4. **OF promo campaign convention.** Standard naming: "IG_Bot_<creator-handle>". OFM creates per creator at onboarding.
5. **Stripe product for auto-invoice.** Subscription product with metered billing, charged on the 1st based on previous month's attribution. EZJ already has Stripe.

Total cost basis to run attribution: ~$25-50/mo (Cloudflare Workers + domain + Supabase Pro if we outgrow free tier). Trivial against expected revenue.

---

## Open questions for Joe + EZJ

1. Do we need real-time attribution (every click triggers a dashboard update), or batch (daily refresh)? Batch is cheaper and simpler. Recommend batch for V1.4.
2. Do we share raw conversation transcripts with the OFM, or only aggregated funnel metrics? Recommend aggregated by default, with a "view 10 sample chats with PII redacted" feature.
3. Do we bill creators monthly or quarterly? Monthly is cleaner cash flow. Quarterly is less invoicing overhead. Recommend monthly.
4. What happens if an OF promo gets churned (sub cancels after week 1)? Do we refund the 15% we already invoiced? Recommend NO refund on V1 (industry standard for chatter teams is similar); revisit at scale.

---

## The TL;DR

**Yes, we can do solid attribution.** It's a 4-layer stack:
1. Bot funnel events to Supabase
2. Tracked short link with click logging
3. OF promo campaign as the billing source of truth
4. Cross-reference for confidence

Total build: ~4-5 days over the first 30 days of Harvey's deploy. Total ops cost: $25-50/mo. The dashboard becomes a sales asset, not just an internal tool.

We don't need OF to give us an API. We engineer around the constraint using OF's own native promo system + our own short link layer. This works.

We should NOT deploy to Harvey's first creator without at minimum Layer 2 + Layer 3 in place. Layer 1 + Layer 4 can come within the first week. Otherwise the first billing cycle has nothing to point at and the rev-share story collapses.
