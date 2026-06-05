# CLAUDE.md — OFM IG DM Agent (Productized Service)

Productized AI service offering for OnlyFans Management agencies (OFMs). Converts an OF creator's Instagram followers into paying OF subscribers through automated, on-brand, human-feeling DM conversations. Sold to OFM agencies (and direct to top-1% solo creators) as a managed service: setup fee plus performance share on attributable subs.

This is **work ON the business** (under `agency/products/`), peer of `agency/lead_acquisition/` and `agency/marketing/`. It is not a client deliverable; it is an agency offering that we sell.

## Read First
- `context.md` in this folder. ICP, offer, pricing, platform-safety constraints, ethical posture.
- `phases/README.md`. The execution playbook for building V1 and shipping the pilot.
- `deliverables/source_joe_auramax_system_prompt.md`. The framework we are adapting.
- `/Users/Ethan/.claude/plans/all-right-look-this-playful-hanrahan.md`. The approved plan that scoped this build.

## Anchor Client
**Harvey Anger / Monetize.me** — OFM agency, 12 creators, soft yes pending partner Tom's approval. See `clients/harvey/meetings/2026-05-31_strategy_session.md` and `clients/harvey/meetings/2026-06-02_pitch_call.md`. Harvey is the pilot bed. He pre-existed this product; we are layering the IG bot on top of the onboarding-form scope.

## Status (as of 2026-06-06)
- Plan approved. Folder scaffolded. Source workflow archived.
- Open: confirm Tom's status on Harvey's $700 onboarding form before pitching the bot upsell.
- Open: rewrite system prompt (Ruby → OFM persona), 7 phases collapsed to a 4-phase IG-to-OF-sub flow.
- Open: clone n8n workflow into `n8n.ezjonline.com`, rewire credentials and webhook path.
- Open: pricing finalization gated on `/hormozi pricing` run.

## Hard Constraints (platform safety, never violate)

1. **No explicit sexual content in IG DMs.** Meta TOS. All explicit material lives behind the OF paywall. The IG DM stays suggestive at most. Build this into the system prompt as a hard ban.
2. **No cold-DM outbound.** ManyChat is Meta-whitelisted only for user-initiated conversations. Every flow must trigger from the user (story react, comment trigger, follow, opener message they sent).
3. **AI disclosure on the exact trigger phrases only.** Same pattern as Joe's Ruby prompt. Adapted identity: "I'm her assistant who runs her DMs while she's shooting." Not the creator pretending to be human; an explicit assistant persona.
4. **18+ age gate at Phase 0.** Legal requirement. Hard disqualify under-18 with a warm exit (link to free public content, no further engagement).
5. **No dashes, em dashes, or en dashes in any output.** Universal Claudia rule, also a useful "AI tell" we strip out for naturalness.
6. **Do NOT build V2 on-platform OF chatter without legal review.** OF TOS bans bots on the platform itself. The IG front-end is policy-safe; the on-platform layer is not. V2 is gated on lawyer review or an official OF chatbot API.

## Deliverables Structure (standard for every productized service)

- `context.md` — durable constraints, ICP, offer, pricing, platform-safety constraints.
- `phases/` — execution system. Command center README + one playbook file per build deliverable, numbered in build order.
- `deliverables/` — finished OUTPUT assets. The system prompt, the n8n workflow, the ManyChat setup guide, the offer doc.

## Reusable patterns this product depends on

- n8n REST API access at `n8n.ezjonline.com` (see memory `reference_n8n_api_access.md`)
- ManyChat custom-field architecture (extracted from Joe's source)
- Google Docs knowledge-base tool pattern (per-creator doc, swappable)
- Hormozi-pricing skill (for offer design in Phase 3 of the build)

## Memory & Continuity

Update memory after meaningful milestones (pilot deployed, first attributable sub, first sale to a non-Harvey OFM, pricing locked).
