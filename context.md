# OFM IG DM Agent — Context

Durable context for the productized service. Update when ICP, offer, or platform constraints change.

## What this is

An AI-driven Instagram DM conversion system for OnlyFans creators. The bot impersonates the creator (or her "assistant who runs her DMs") in IG DMs, builds rapport with engaged followers, then converts them into paying OF subscribers. Optionally hands the warmed lead off to the OFM's on-platform chatter team for the upsell. We sell the system, the setup, and the ongoing optimization as a managed service.

## The wedge (why this works)

Three structural realities of OFM economics:

1. **OFMs spend $1.5k-$3k per creator per month on Filipino chatter teams** who work the on-platform DMs (where the real money is, custom content + sexting + pay-per-view). They don't have the bandwidth to also work IG DMs at scale. IG inbound is mostly ignored or auto-replied with a static link.
2. **A creator's IG DMs are where the highest-intent subs come from.** A follower who DMs has more intent than a cold ad click. But responding to all of them in the creator's voice doesn't scale with humans.
3. **The bot replaces a $0 layer (currently un-staffed) and creates incremental subs.** This is not a "fire your chatters" pitch (which would meet defensiveness). It's a "we'll catch the subs you're losing in IG DMs" pitch.

## ICP

**Primary:** OFM agencies with 5-30 creators, where:
- Creators average $5k-$50k/mo on OF (mid-tier, room to grow)
- Each creator has 5k-100k IG followers
- The agency owner is technical-friendly enough to set up ManyChat and integrate a webhook
- The agency is already paying for chatter teams (proves they invest in conversion ops)

**Secondary:** Top-1% solo creators ($50k+/mo) who manage their own DMs and would buy the bot as a tool.

**Out-of-scope for V1:** Beginner creators (<$5k/mo, not enough volume), and creators in markets where OF is restricted.

## The offer (placeholder, finalize via `/hormozi pricing` in Phase 3)

**Setup fee:** ~$2,000 per creator. Covers:
- ManyChat app build and custom-field setup
- Per-creator knowledge base doc (Google Doc with voice samples, niche, sub price, custom-content rules)
- System prompt customization for her persona
- n8n webhook provisioning
- First 7 days of live monitoring and prompt iteration

**Performance share:** ~10-15% of new OF subscription revenue attributable to bot-driven subs. Tracked via dedicated UTM/promo code on the OF sub link.

**Founder rate for Harvey (case study trade):** 5% performance + $1,000 setup for his first 3 creators in exchange for testimonial rights, Loom case-study footage, and a written quote we can use in cold outbound.

## Anchor client

**Harvey Anger / Monetize.me** — UK-based, 12 creators, partner Tom. Soft yes 2026-06-02. Memory: `project_harvey_monetize_me_2026-06-02.md`. Open status check needed on Tom's $700 onboarding-form approval before pitching the bot upsell.

## Platform-safety posture (non-negotiable)

| Layer | Risk | Mitigation |
|-------|------|------------|
| Meta IG DM automation | Account restriction if cold-DMing or violating opt-in rules | Use ManyChat (Meta-whitelisted partner). Only user-initiated flows (story react, comment, follow, inbound DM). No outbound cold messages. |
| Meta IG content policy | Account ban if explicit content shared in DMs | Hard ban in system prompt. Suggestive language OK; explicit content lives only behind the OF paywall. Built into the prompt's "ABSOLUTE HARD LIMITS" section. |
| OF terms on referrals | None. OF welcomes IG-driven subs. | Standard IG-to-OF funnel is the entire OF growth playbook. Front-end IG bot is fully policy-safe. |
| OF terms on on-platform bots | OF TOS bans bots on the platform itself | V2 (on-platform chatter) is gated on lawyer review or an OF chatbot API. Do not build until then. |
| Persona ethics (bot impersonates creator) | Industry-standard practice; human chatters already do this | Disclosed honestly to the buyer (OFM/creator) in the offer doc. Not disclosed to the end fan, which matches industry norm. AI-disclosure protocol fires if the fan explicitly asks "are you a bot." |
| Payment processor risk on OFM | OFMs are high-risk merchant category | Not our concern at V1; we don't process payments for the OFM. Setup fee and performance share both invoice through EZJ Online LLC Stripe + Wise. |

## Decision log

- 2026-06-06: Plan approved. V1 scope = front-end IG DM bot only. V2 on-platform chatter parked.
- 2026-06-06: Harvey is the pilot. One of his lower-stakes creators (5k-50k IG follower range) will be the first deployment.
- 2026-06-06: Pricing finalization deferred to `/hormozi pricing` run after pilot is technically operational.
- 2026-06-06: Folder convention = `agency/products/ofm_ig_dm_agent/`. New `agency/products/` parent dir established for future productized services.

## Open loops

- ❓ Tom's approval on Harvey's $700 onboarding-form project (precondition for cleanly pitching the bot upsell).
- ❓ Which Harvey creator becomes the pilot (Harvey to nominate).
- ❓ Pricing finalization via `/hormozi pricing`.
- ❓ Per-creator knowledge base doc template (build during Phase 2).
- ❓ Attribution mechanism for performance-share tracking (UTM on OF link vs ManyChat tag vs OF promo code).
