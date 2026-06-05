# Phase 1: Adapt Joe's n8n workflow for OFM

Status: 🔄 In progress (started 2026-06-06)
Owner: EZJ + Claudia
Output: `../deliverables/n8n_workflow_ofm_v1.json`, `../deliverables/system_prompt_v1.md`

## Step 1.1: Save source JSON ✅ Locked · ✔️ Done

Done. Saved verbatim to `../deliverables/source_joe_auramax_workflow.json` with long-form text fields extracted into `source_joe_auramax_system_prompt.md` for diff-readability. Joe's workflow is the source of truth; do not edit those files.

## Step 1.2: Rewrite the system prompt for OFM ✅ Locked · 🔄 In progress

This is the real work. Joe's prompt is built around a 7-phase qualifier that books a 15-min audit call. The OFM flow has different intent (drive an OF sub), different persona (creator's assistant, not coach's assistant), and different psychology (emotional connection and fantasy, not pain and transformation proof).

Source → target mapping (the table from the approved plan):

| Phase | Joe (AuraMax) | OFM equivalent |
|-------|---------------|----------------|
| 0 | Country + age qual | 18+ confirm (legal). Country only matters for spend power, broader Tier list. |
| 1 | Engagement / rapport | Warm flirt, mirror, react to the entry trigger (story react, comment, follow) |
| 2 | Discovery (goal/pain) | Connection. What do they like, why are they here. Emotional need (loneliness, fantasy, novelty, validation). |
| 3 | Pattern + vision | Tease exclusive content, hint at the paywall, normalize the buy |
| 4 | Social proof | "What my subs say" preview, creator-supplied teaser asset, "you'd like this" frame |
| 5 | Call positioning | OF link pitch with a time-limited bonus (first DM free, custom content discount) |
| 6 | Booking confirmation | Confirm sub, welcome to OF, hand off to on-platform chatter team |

Persona rules to encode:
- First person AS the creator's assistant. Not the creator herself.
- Empathy and emotional connection over feature-pushing.
- No dashes (also Claudia's universal rule).
- AI disclosure on the exact trigger phrases only (same pattern as Joe).
- HARD BAN on explicit sexual offers in DMs (Meta TOS). Suggestive language OK, explicit content lives behind the paywall only.
- Knowledge_base tool calls before any creator-specific question (her bio, niche, sub price, custom-content rules).

Tool calls (rename + retarget Joe's 5 tools):
- `save_qualification_data` → age 18+, country
- `save_discovery_data` → vibe, interests, why-they-followed, urgency-to-sub
- `save_subscription_data` (replaces save_booking_data) → subbed-yes/no, tier, timestamp
- `apply_tag` → Trust_Asset_Sent, OF_Link_Pitched, Subscribed, AI_Detection_Triggered, Disqualified
- `update_conversation_state` → phase + summary, unchanged pattern

Output goes to `../deliverables/system_prompt_v1.md`. We then paste this into the n8n AI Agent node's `systemMessage` field.

## Step 1.3: Rewrite the message formatter prompt ✅ Locked · ⬜ Not started

The "Message a model" node splits the AI Agent's output into 1-6 IG-style messages. Keep the formatter logic identical; only update:
- Drop the AuraMax YouTube canonical-link rule
- Add a generic "preserve all URLs verbatim" rule (the per-creator OF link must round-trip exactly)
- Update the example link in the system message

Output goes to `../deliverables/formatter_prompt_v1.md`.

## Step 1.4: Rewire n8n credentials and webhook ✅ Locked · ⬜ Not started

Use n8n REST API at `n8n.ezjonline.com` with `N8N_API_KEY` env var (per memory `reference_n8n_api_access.md`).

Rewires required:
- **AI Model:** swap GPT-5.4 + Joe's OpenAI cred for current Claude model (Sonnet 4.6 default; Opus 4.7 only if margin justifies). Check current model pricing before locking.
- **AI Model1 (fallback):** swap Kachi's OpenAI cred for EZJ's OpenAI fallback (in `.env` as `OPENAI_API_KEY`).
- **Knowledge base:** swap AuraMax Google Doc URL for per-creator doc URL (set in Step 2.3).
- **Memory:** swap session-key prefix `4{{ ig_username }}5` for a cleaner `ofm_<creator-handle>_{{ ig_username }}` so multiple creators on the same n8n don't collide.
- **All 5 tool nodes (ManyChat custom-field setters):** swap Joe's ManyChat bearer-auth cred for the per-creator ManyChat bearer (created in Step 2.2).
- **Send Flow:** swap `flow_ns` for the per-creator ManyChat send-message flow id.
- **Webhook path:** new path namespaced `/webhook/ofm-ig-dm-<creator-handle>`.
- **Workflow name:** rename to `OFM IG DM Agent V1 — <creator-handle>`.

Output: working JSON saved to `../deliverables/n8n_workflow_ofm_v1.json`. Import via n8n REST API (`POST /api/v1/workflows`).

## Verification before Phase 2 begins

- [ ] System prompt v1 written and reviewed by EZJ
- [ ] Formatter prompt v1 written
- [ ] n8n workflow imported clean, all nodes resolve, no broken credentials
- [ ] Mock curl POST to the webhook returns 200
- [ ] AI Agent node responds to a test message without erroring on missing custom fields
