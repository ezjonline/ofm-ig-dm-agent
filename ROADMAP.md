# Roadmap

The full build plan across both prongs. Owner-tagged, time-boxed, dependency-mapped, and structured so we can bring in more contributors (Joe, AI homies, future hires) without losing the thread.

**Last updated:** 2026-06-06
**Current phase:** Phase 0 (Foundation + Harvey prep)
**Next milestone:** Harvey pilot creator live (target: 2026-06-20)

---

## How to read this

- **Phases** = sequential milestones (you can't start Phase 1 until Phase 0 lands)
- **Workstreams** = parallel tracks that run across phases (sales runs in every phase, content generation builds across phases 2-6)
- **Owners** = who's responsible. Single owner per task. No "Joe + EZJ" both doing the same thing.
- **Status:** ⬜ not started · 🔄 in progress · ✅ done · ❓ blocked

If you're a new contributor: read this file, the README, GTM_STRATEGY, ATTRIBUTION, PHASE_2_AI_CREATORS. That's the whole picture in ~60 minutes of reading.

---

## Phases at a glance

| Phase | Timeframe | Goal | Exit when |
|---|---|---|---|
| **P0** | Week 1 (June 6-13) | Voice polish, demo assets, Harvey closure | Demo Loom + Harvey verbal yes |
| **P1** | Week 2-4 (June 13 - July 3) | Harvey pilot creator live with full attribution | First sub attributed to bot |
| **P2** | Week 5-8 (July) | Multi-OFM outreach + 2-3 new closes | $5k+ MRR from Prong 1 |
| **P3** | Week 6-12 (parallel) (July-Sept) | Phase 2 (AI creator) infra built | Mia visual library ready |
| **P4** | Week 12-16 (Sept-Oct) | Mia goes live as AI creator | First Mia OF sub |
| **P5** | Month 4-6 (Oct-Dec) | Maya (V2 on-platform) + persona #2 | Mia at $20k/mo, persona #2 in build |
| **P6** | Month 6+ | Scale Prong 2, wind down Prong 1 | 3+ AI creators live, $30k+ MRR |

---

## Workstreams (run across phases)

| Workstream | Description | Primary owner |
|---|---|---|
| **WS-1: Bot Voice + Persona** | Bella's prompt, Mia's KB, character depth, anti-pattern tuning | **Joe** |
| **WS-2: Production Infra** | n8n, ManyChat wiring, deploy scripts, per-creator onboarding | **EZJ + Claudia** |
| **WS-3: Attribution + Dashboard** | Supabase events, short link, OF promos, OFM-facing dashboard | **Claudia + EZJ** |
| **WS-4: Sales + Outreach** | Outreach kit, Loom demos, cold DMs, OFM relationship management | **EZJ** |
| **WS-5: Phase 2 Content + Identity** | AI persona generation, visual assets, IG growth, OF launch | **EZJ + future contributor + Claudia** |

---

# Phase 0: Foundation (Week 1, June 6-13)

**Goal:** Get the demo asset polished enough to pitch Harvey + 5 other OFMs cold, and lock in Harvey's pilot creator.

| # | Task | Owner | Status | Notes |
|---|---|---|---|---|
| 0.1 | Voice polish: Bella's prompt v1.1 with deeper flirt cadence | **Joe** | 🔄 | Joe's first PR after he accepts the GitHub invite |
| 0.2 | Mia's KB expansion: 50+ voice samples, 5+ archetype handling examples | **Joe** | 🔄 | In `simulator/mia_test_creator.md` |
| 0.3 | Anthropic credits topped up so we can swap gpt-4o → Sonnet 4.6 | **EZJ** | ❓ | One-line config swap in deploy script after credits land |
| 0.4 | Sonnet 4.6 swap in `deploy_full_simulator.py` | **Claudia** | ⬜ | After 0.3 |
| 0.5 | Create OF test account ("Mia" or other) | **EZJ** | ⬜ | ~5 min; place 2-3 placeholder posts so link doesn't go to empty page |
| 0.6 | Create @mia.everyday IG (or available handle) | **EZJ** | ⬜ | Business profile, link to new FB Page |
| 0.7 | 20 anchor images for Mia (Flux 1.1 Pro via fal.ai) | **Claudia + EZJ** | ⬜ | Defines her visual identity; reused in Phase 3 too |
| 0.8 | Post the first 5-10 IG posts on @mia.everyday (backdated dates) | **EZJ** | ⬜ | Soft launch, looks 4-6 weeks old |
| 0.9 | Ping Harvey on Tom approval + pilot creator nomination | **EZJ** | ⬜ | Direct Telegram, 1 message, no follow-up until reply |
| 0.10 | Record 90-second demo Loom (chat.html walkthrough + 30s pitch) | **EZJ** | ⬜ | Demo asset for both Harvey close + cold OFM outreach |
| 0.11 | Branch protection rule on `ezjonline/ofm-ig-dm-agent` | **EZJ** | ✅ | Already done |
| 0.12 | Add Joe as GitHub collaborator | **EZJ** | ⬜ | `gh repo invite ezjonline/ofm-ig-dm-agent <username> --permission write` |

**Phase 0 exit:** Loom recorded, Harvey verbal yes on a pilot creator OR 5 cold OFM DMs sent with positive replies.

---

# Phase 1: Harvey Pilot (Week 2-4, June 13 - July 3)

**Goal:** First real creator running Bella live on her IG with attribution. First billing cycle proves the rev-share model works.

## P1 Workstreams

### WS-2: Production Deploy

| # | Task | Owner | Status |
|---|---|---|---|
| 1.1 | Harvey nominates pilot creator (handle, OF URL, sub price, existing IG follower count) | **EZJ** | ⬜ |
| 1.2 | Per-creator KB doc built (Google Doc, voice samples from real DMs) | **EZJ + creator** | ⬜ |
| 1.3 | Clone production n8n workflow template, rewire `<CREATOR_HANDLE>` placeholders | **Claudia** | ⬜ |
| 1.4 | ManyChat app created on pilot creator's IG | **EZJ + Harvey** | ⬜ |
| 1.5 | 19 ManyChat custom fields built (per `manychat_setup_guide.md`) | **EZJ** | ⬜ |
| 1.6 | 4 ManyChat trigger flows: story-react, comment, cold DM, default-reply | **EZJ** | ⬜ |
| 1.7 | ManyChat External Request action wired to n8n production webhook | **EZJ** | ⬜ |
| 1.8 | ManyChat Send Flow + custom field passthrough for split messages | **EZJ** | ⬜ |
| 1.9 | End-to-end smoke test from burner IG | **EZJ + Claudia** | ⬜ |
| 1.10 | Creator reviews 10 sample conversations, signs off on tone | **EZJ → creator** | ⬜ |
| 1.11 | Go live, monitor first 24 hours | **EZJ** | ⬜ |

### WS-3: Attribution Stack (V1.1 - V1.3)

| # | Task | Owner | Status |
|---|---|---|---|
| 1.12 | Supabase project created, schema for `attribution_events` table | **Claudia** | ⬜ |
| 1.13 | n8n branch added to OFM workflow: each tool call → Supabase row | **Claudia** | ⬜ |
| 1.14 | Cloudflare Workers redirector deployed at chosen short link domain | **Claudia** | ⬜ |
| 1.15 | Short link logs click → Supabase | **Claudia** | ⬜ |
| 1.16 | OF promo campaign created for pilot creator ("IG_Bot_<creator>") | **EZJ + Harvey** | ⬜ |
| 1.17 | Bella's prompt updated to use short link instead of bare OF URL | **Claudia** | ⬜ |

### WS-1: Voice (continues from P0)

| # | Task | Owner | Status |
|---|---|---|---|
| 1.18 | Daily review of first 7 days of real conversations, prompt iteration | **Joe** | ⬜ |
| 1.19 | Per-creator voice tuning: adapt to her actual voice samples | **Joe** | ⬜ |

**Phase 1 exit:** Pilot creator has ≥5 attributable subs in first 30 days; first invoice sent to Harvey.

---

# Phase 2: Multi-OFM Outreach (Week 5-8, July)

**Goal:** Scale from 1 OFM (Harvey) to 3-4 OFMs. Cash flow becomes real.

## P2 Workstreams

### WS-4: Outreach

| # | Task | Owner | Status |
|---|---|---|---|
| 2.1 | Polish offer doc with Harvey case study numbers | **EZJ** | ⬜ |
| 2.2 | Build OFM lead list (50 targets from IG, X, Discord) | **EZJ + Claudia** | ⬜ |
| 2.3 | Outreach DM template (3-message warm-cold cadence) | **EZJ + Joe** | ⬜ |
| 2.4 | Cal.com booking page for "OFM IG DM Audit" | **EZJ** | ⬜ |
| 2.5 | Send 50 personalized Looms/DMs over 2 weeks | **EZJ** | ⬜ |
| 2.6 | Discovery calls with replies (target 8-12 calls) | **EZJ** | ⬜ |
| 2.7 | Close 2-3 new OFMs | **EZJ** | ⬜ |

### WS-3: Attribution (V1.4 - V1.5)

| # | Task | Owner | Status |
|---|---|---|---|
| 2.8 | Retool dashboard MVP (funnel + revenue + commission owed) | **Claudia** | ⬜ |
| 2.9 | Per-OFM tenant access (login URL per OFM) | **Claudia** | ⬜ |
| 2.10 | Stripe metered billing product, auto-invoice on the 1st | **EZJ + Claudia** | ⬜ |
| 2.11 | Cross-reference engine (Layer 4 confidence scoring) | **Claudia** | ⬜ |

### WS-2: Multi-Creator Deploy

| # | Task | Owner | Status |
|---|---|---|---|
| 2.12 | Build `scripts/onboard_creator.py` (automates the 90-min ManyChat setup as much as possible) | **Claudia** | ⬜ |
| 2.13 | Onboard 6-12 new creators across the new OFMs | **EZJ + Claudia** | ⬜ |
| 2.14 | Per-creator monitoring dashboard (internal-only) | **Claudia** | ⬜ |

**Phase 2 exit:** $5k+ MRR from Prong 1, 4+ OFMs onboarded, 12+ creators live with Bella.

---

# Phase 3: AI Creator Infrastructure (Week 6-12, parallel to P2, July-September)

**Goal:** Build the content + identity pipeline for Phase 2 (AI creators). Mia is the first persona; the pipeline is the reusable product.

This phase runs in **parallel** with P2. EZJ time-splits 70% sales / 30% Phase 3. Claudia (me) carries most of Phase 3 lifting; Joe contributes on voice/persona side.

## P3 Workstreams

### WS-5: Visual Identity (Mia)

| # | Task | Owner | Status |
|---|---|---|---|
| 3.1 | `personas/mia/identity.md` written (name, age, niche, backstory, voice DNA) | **Joe** | ⬜ |
| 3.2 | `personas/mia/visual_brief.md` (anchor images, style refs, mood board) | **EZJ + Joe** | ⬜ |
| 3.3 | Image gen API integration (fal.ai for Flux 1.1 Pro) | **Claudia** | ⬜ |
| 3.4 | LoRA training pipeline for consistent face/body across all photos | **Claudia + EZJ** | ⬜ |
| 3.5 | 50-100 IG-safe photos generated (lifestyle, gym, photoshoot, cafe, beach) | **Claudia + EZJ** | ⬜ |
| 3.6 | 200-500 OF-safe photos generated (paywall content, suggestive not explicit) | **Claudia + EZJ** | ⬜ |
| 3.7 | 20-50 short videos via Sora 2 / Veo 3 / Kling with LoRA applied | **Claudia + EZJ** | ⬜ |
| 3.8 | Persona consistency QA: 90%+ of generated content recognizable as same person | **EZJ + Joe** | ⬜ |

### WS-5: IG Growth

| # | Task | Owner | Status |
|---|---|---|---|
| 3.9 | @mia.everyday IG fully populated with 30-50 backdated posts | **EZJ** | ⬜ |
| 3.10 | Daily story automation (n8n cron) | **Claudia** | ⬜ |
| 3.11 | Caption generation in Mia's voice (Sonnet) | **Claudia + Joe** | ⬜ |
| 3.12 | Organic growth tactics: cross-post to TikTok + X | **EZJ** | ⬜ |
| 3.13 | Paid follower acquisition (test 3 services, pick one) | **EZJ** | ⬜ |
| 3.14 | Engagement automation: ManyChat for IG comments + DMs (using existing Bella) | **EZJ + Claudia** | ⬜ |
| 3.15 | Target: 5k IG followers before OF launch | **EZJ** | ⬜ |

### Legal / Compliance

| # | Task | Owner | Status |
|---|---|---|---|
| 3.16 | Lawyer consultation: AI creator disclosure requirements (IG + OF) | **EZJ** | ⬜ |
| 3.17 | Decide disclosure policy: explicit AI labeling vs implied | **EZJ + Joe** | ⬜ |
| 3.18 | OF account creation timing review (after IG hits 5k) | **EZJ** | ⬜ |

**Phase 3 exit:** Mia has 5k IG followers, OF account ready to launch, content library can sustain 3-5 posts/week and 1-2 paywall drops/week.

---

# Phase 4: Mia Goes Live (Week 12-16, September-October)

**Goal:** First AI creator generating real OF revenue. Validates the Prong 2 model.

## P4 Workstreams

### WS-5: OF Launch

| # | Task | Owner | Status |
|---|---|---|---|
| 4.1 | Mia OF account created, verified, populated with launch content | **EZJ** | ⬜ |
| 4.2 | Sub price + promo configured ($9.99/mo + 50% off first month) | **EZJ** | ⬜ |
| 4.3 | OF promo campaign created for "IG_Bot_Mia" | **EZJ** | ⬜ |
| 4.4 | Bella's IG-to-OF funnel activated on @mia.everyday | **EZJ + Claudia** | ⬜ |
| 4.5 | Custom KB doc deployed for Mia (using template, just like a real creator deploy) | **EZJ + Joe** | ⬜ |
| 4.6 | Launch announcement post on @mia.everyday | **EZJ** | ⬜ |
| 4.7 | First 30-day monitoring + iteration | **EZJ + Joe + Claudia** | ⬜ |

### WS-5: Maya V2 Development (parallel)

| # | Task | Owner | Status |
|---|---|---|---|
| 4.8 | Maya persona prompt (Bella's on-platform sister) | **Joe** | ⬜ |
| 4.9 | Chrome extension scaffold (Manifest V3) | **Claudia** | ⬜ |
| 4.10 | OF DOM selector mapping (read the active chat thread) | **Claudia** | ⬜ |
| 4.11 | n8n on-platform webhook + Maya agent | **Claudia** | ⬜ |
| 4.12 | PPV catalog data structure (per creator) | **Claudia + EZJ** | ⬜ |
| 4.13 | Side panel UI in extension (draft reply + insert button) | **Claudia** | ⬜ |
| 4.14 | Smoke test with Mia's OF account | **EZJ** | ⬜ |

**Phase 4 exit:** Mia at $5-15k/mo OF revenue. Maya V2 internal-only validated.

---

# Phase 5: Maya V2 + Persona #2 (Month 4-6, October-December)

**Goal:** Prong 2 revenue > Prong 1 revenue. Begin scaling.

| # | Task | Owner | Status |
|---|---|---|---|
| 5.1 | Maya V2 deployed to Mia's OF (we use it ourselves) | **EZJ** | ⬜ |
| 5.2 | Measure throughput uplift: PPV revenue, tip volume, retention | **Claudia** | ⬜ |
| 5.3 | If Maya works internally: offer Maya V2 as Prong 1 add-on to existing OFMs (+10% rev share on on-platform revenue) | **EZJ** | ⬜ |
| 5.4 | Mia hits $20-30k/mo OF revenue | **All** | ⬜ |
| 5.5 | Persona #2 spec locked (different niche, e.g. fitness-only or alt/punk) | **Joe + EZJ** | ⬜ |
| 5.6 | Persona #2 visual asset generation (reuses pipeline from P3) | **Claudia + EZJ** | ⬜ |
| 5.7 | Persona #2 IG warm-up begins | **EZJ** | ⬜ |

**Phase 5 exit:** Prong 2 MRR > Prong 1 MRR. Persona #2 in IG warm-up phase.

---

# Phase 6: Scale (Month 6+, January 2027+)

**Goal:** Real company. 3-5 AI creators live, content pipeline fully automated, possibly bring in contractors.

| # | Task | Owner | Status |
|---|---|---|---|
| 6.1 | 3-5 AI creators live, total OF revenue $50-100k/mo | **All** | ⬜ |
| 6.2 | Wind down Prong 1 OR keep as cash-flow side biz | **EZJ** | ⬜ |
| 6.3 | Hire/contract: content editor, ops manager, possibly chatter for human-in-the-loop on top-tier personas | **EZJ** | ⬜ |
| 6.4 | Build: persona-spawn automation (full pipeline from "new persona" command to "OF live" in 4 weeks) | **Claudia** | ⬜ |
| 6.5 | Marketing site for Prong 2 (the company brand, not the personas) | **EZJ + Claudia** | ⬜ |

**Phase 6 exit:** $100k+ MRR. Real company status.

---

# Owner load-balancing

Where each person's time goes by phase:

### Joe (voice + persona)
- P0: 100% voice polish (his entry contribution)
- P1: 80% real-conversation review + iteration / 20% Mia depth
- P2: 50% real-conversation iteration / 50% Mia voice
- P3-P4: 60% Mia / Maya prompts / 40% real-OFM voice maintenance
- P5+: shift to Prong 2 persona work (multiple personas)

### EZJ (sales + business + infra co-pilot)
- P0: 50% sales prep / 30% test accounts / 20% infra
- P1: 70% Harvey deploy / 30% backfill
- P2: 70% outreach + sales / 30% multi-creator onboarding
- P3-P4: 50% sales / 30% Phase 2 build / 20% legal
- P5+: 30% sales / 70% Prong 2 ops

### Claudia (me, technical execution)
- P0: 30% prompt + sim improvements / 70% infra (n8n cleanup, paginated fixes already done, Sonnet swap, deploy script polish)
- P1: 80% production deploy + attribution stack / 20% sim maintenance
- P2: 60% dashboard + auto-invoice / 40% onboarding automation
- P3-P4: 70% Phase 2 build (content gen, IG automation, Chrome extension) / 30% Prong 1 ops
- P5+: 90% Phase 2 / 10% Prong 1

---

# Where you could bring in more AI homies

Specific high-leverage roles you could delegate to a contributor (paid or AI-agent-driven):

| Role | What they own | When to bring in |
|---|---|---|
| **Content QA reviewer** | Daily review of generated photos for persona consistency, flag drift | P3 onwards (when image gen volume scales) |
| **IG account warmer** | Manual organic engagement (likes, comments, follows in niche) on Mia's IG | P3 (during 4-6 week warm-up) |
| **OFM lead researcher** | Build the 50-OFM target list, enrich with revenue estimates and contact info | P2 (right before outreach blast) |
| **Cold DM personalizer** | Per-OFM custom Loom thumbnails + opener line + CTA | P2 outreach phase |
| **Customer success manager** | Weekly check-ins with onboarded OFMs, surface bot issues, upsell to Maya V2 | P2+ once we have 3+ OFM clients |
| **Compliance / legal liaison** | Stay current on IG/OF policy changes, AI disclosure rules, payment processor risk | P3 onwards (continuous) |
| **Persona writer** | Beyond Joe's voice work, develop each persona's lore, IG captions, story scripts | P3 onwards (Mia first, scale to multiple personas) |
| **Paid ads operator** | Run IG/TikTok paid follower acquisition for each persona | P3-P4 IG warm-up |

For AI-agent delegation (no human, just Claudia or another agent): the persona-writer, content QA reviewer, OFM lead researcher, and cold DM personalizer can all be agents. The IG account warmer needs to be a human (Meta detects bot-style engagement).

---

# Open decisions blocking forward motion

These are EZJ decisions I (or Joe) can't make. Each one unblocks the next phase.

| Decision | Phase blocked | Recommendation | Status |
|---|---|---|---|
| Anthropic credits top-up | P0 | Top up $200, swap to Sonnet 4.6 | ❓ |
| OF test account name | P0 | "Mia" (matches simulator persona) | ❓ |
| IG handle for Mia | P0 | `@mia.everyday` (check availability) | ❓ |
| Short link domain | P1 | `bellaroutes.com` shared, per-creator paths | ❓ |
| Supabase project create | P1 | New dedicated project (separate from claudia) | ❓ |
| Stripe billing cadence | P2 | Monthly, auto-invoice on the 1st | ❓ |
| Lawyer for AI disclosure | P3 | Book consultation when Mia hits 1k IG followers | ❓ |
| Image gen platform | P3 | fal.ai with Flux 1.1 Pro | ❓ |
| Video gen platform | P3 | Veo 3 or Sora 2, pick when budgeting | ❓ |
| Persona #2 niche | P5 | Decide based on what works for Mia | ❓ |

Drop a decision for any of these and I'll execute on it. Multiple decisions in one message is fine.

---

# Risks worth surfacing now

So we can plan around them, not be surprised.

| Risk | Phase impact | Mitigation |
|---|---|---|
| Harvey kills the deal entirely | P1 stalls | Go cold-outbound to other OFMs immediately, use Mia (in-progress) as demo |
| Meta bans @mia.everyday during warm-up | P3-P4 stalls | Multi-account strategy (have a backup handle warming up), avoid aggressive automation in first 30 days |
| OF flags an AI creator account | P4 stalls | Lawyer review BEFORE launch (P3), comply with disclosure, diversify (1 persona until we know the rules) |
| Joe leaves the project | WS-1 stalls | EZJ + Claudia can carry voice work, but slower; document everything Joe knows about the persona |
| EZJ runs out of bandwidth | All slows | Delegate aggressively per the "AI homies" section above |
| Anthropic / OpenAI prices spike | All ops cost goes up | Cache prompts heavily, consider Groq / OpenRouter for fallback, swap to smaller models for non-creative work |
| OF or Meta API changes break the flow | P1+ | Monitoring + alerting on the n8n workflow; manual fallback plan |

---

# Today's next actions (post-this-doc)

For EZJ:
1. Top up Anthropic credits
2. Send Joe the GitHub invite (`gh repo invite ezjonline/ofm-ig-dm-agent <username> --permission write`)
3. Decide: OF + IG handle for Mia (test or production-bound?)
4. Ping Harvey with Tom status check
5. Create Supabase project (free tier fine)

For Joe (after accepting invite):
1. Pull the repo, set up `.env` with `OFM_SIM_OWNER=joe`
2. Deploy his sandbox
3. Read GTM_STRATEGY + ATTRIBUTION + PHASE_2_AI_CREATORS + this ROADMAP
4. First PR: voice tightening pass on `deliverables/system_prompt_v1.md`

For Claudia (me):
1. Sonnet 4.6 swap as soon as credits land
2. Start scaffolding `personas/mia/` and `content_engine/`
3. Build Supabase schema for `attribution_events` once project exists
4. Polish deploy script with better error handling for the pagination edge case
