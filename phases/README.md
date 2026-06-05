# OFM IG DM Agent — Phases Command Center

Productizing the AuraMax IG DM framework into a sellable managed service for OFM agencies. Each numbered file in this folder is one phase of the build. Open the file you are on, expand the current step, do it, collapse it, move to the next.

`phases/` = the HOW. `../deliverables/` = the OUTPUT. `../context.md` = ICP, offer, constraints.

## How to read each file
- ✅ **Locked** — agreed/scoped. Build it.
- 🟡 **Proposed** — Claudia's recommendation. Approve or tweak, then it locks.
- ❓ **Blocked** — waiting on a decision or input (named in the step).
- ⬜ Not started · 🔄 In progress · ✔️ Done

## Phases

| Phase | When | Theme |
|-------|------|-------|
| Phase 1 | this week | Adapt Joe's n8n workflow + rewrite the system prompt for OFM |
| Phase 2 | week 1-2 | Deploy V1 pilot on one of Harvey's creators |
| Phase 3 | week 2 | Run `/hormozi pricing` and finalize the offer doc |
| Phase 4 | week 3+ | Cold outbound to other OFMs once Harvey pilot shows attributable subs |

## Deliverable map

| # | Deliverable | File | Phase | Status |
|---|-------------|------|-------|--------|
| 1 | n8n workflow adapted for OFM | `../deliverables/n8n_workflow_ofm_v1.json` | 1 | ⬜ |
| 2 | OFM-adapted system prompt | `../deliverables/system_prompt_v1.md` | 1 | ⬜ |
| 3 | ManyChat setup guide (per-creator) | `../deliverables/manychat_setup_guide.md` | 2 | ⬜ |
| 4 | Per-creator knowledge base doc template | `../deliverables/creator_knowledge_base_template.md` | 2 | ⬜ |
| 5 | Offer doc (final pricing + scope) | `../deliverables/offer_doc.md` | 3 | ⬜ |
| 6 | Cold outreach asset (Loom script + DM templates) | `../deliverables/outreach_kit.md` | 4 | ⬜ |

## Current focus

> 🔄 Phase 1: rewrite the system prompt for the OFM persona. This is the real work; the workflow JSON is mostly a credential and webhook rewire.

## Open decisions blocking later work

- ❓ Tom's status on Harvey's $700 onboarding-form project. Confirm before pitching the bot upsell.
- ❓ Which Harvey creator gets pilot status (Harvey nominates).
- ❓ Pricing finalization (Phase 3 via `/hormozi pricing`).
- ❓ Attribution mechanism for performance share (UTM on OF link vs ManyChat tag vs OF promo code).

---
Plan reference: `/Users/Ethan/.claude/plans/all-right-look-this-playful-hanrahan.md`.
