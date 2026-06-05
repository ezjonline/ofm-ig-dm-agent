# OFM IG DM Agent — Status Map

What's live today, what gets us to the first paid pilot, and what's V2.
Last updated 2026-06-06.

---

## Three lifecycle stages

```
STAGE 1: SIMULATION (NOW — you are here)
┌──────────────────────────────────────────────────────────────────────┐
│  chat.html (your laptop)                                             │
│         │                                                            │
│         │  POST /webhook/ofm-sim-mia                                 │
│         ▼                                                            │
│  ┌─────────────────────────────────────┐                             │
│  │  n8n.ezjonline.com                  │                             │
│  │  Workflow: OFM IG DM Agent SIMULATOR│                             │
│  │  ID: 35xDeYWpYVsCDU6L                │                             │
│  │  ┌───────────────────────────────┐  │                             │
│  │  │ Webhook                       │  │                             │
│  │  │   ↓                           │  │                             │
│  │  │ AI Agent (gpt-4o)             │  │                             │
│  │  │   • System prompt: Bella      │  │                             │
│  │  │   • Mia KB inlined            │  │                             │
│  │  │   • SIM tags instead of tools │  │                             │
│  │  │   ↓                           │  │                             │
│  │  │ Memory (30 turn window)       │  │                             │
│  │  └───────────────────────────────┘  │                             │
│  │             ↓                       │                             │
│  │         JSON response               │                             │
│  └─────────────────────────────────────┘                             │
│         │                                                            │
│         ▼                                                            │
│  chat.html renders Bella's reply as split bubbles                    │
│                                                                      │
│  ✅ What works: full conversation flow, persona, hard limits,         │
│     guardrails (underage, AI disclosure, nude refusal, broke)        │
│  ⚠️ Known issues: gpt-4o dash slip, markdown link format             │
│  ❌ Not wired: ManyChat, Google Docs KB, attribution                 │
└──────────────────────────────────────────────────────────────────────┘

STAGE 2: HARVEY PILOT (next 1-2 weeks, gated on Tom + creator pick)
┌──────────────────────────────────────────────────────────────────────┐
│  Pilot creator's Instagram account                                   │
│         │                                                            │
│         │  Fan sends DM, reacts to story, comments on post           │
│         ▼                                                            │
│  ┌─────────────────────────────────────┐                             │
│  │  ManyChat (Meta-whitelisted)        │                             │
│  │   • Trigger flow fires              │                             │
│  │   • Stores message in custom field  │                             │
│  │   • External Request → n8n webhook  │                             │
│  └─────────────────────────────────────┘                             │
│         │  POST /webhook/ofm-ig-dm-<creator-handle>                  │
│         ▼                                                            │
│  ┌─────────────────────────────────────┐                             │
│  │  n8n production workflow            │                             │
│  │  (cloned from ofm_v1.json template) │                             │
│  │  ┌───────────────────────────────┐  │                             │
│  │  │ Webhook                       │  │                             │
│  │  │   ↓                           │  │                             │
│  │  │ AI Agent (Sonnet 4.6 ideal)   │  │                             │
│  │  │   ├─ Knowledge base tool      │  │  ←  Google Doc per creator  │
│  │  │   ├─ save_qualification_data  │  │  ←  ManyChat custom fields  │
│  │  │   ├─ save_discovery_data      │  │  ←  ManyChat                │
│  │  │   ├─ save_subscription_data   │  │  ←  ManyChat                │
│  │  │   ├─ update_conversation_state│  │  ←  ManyChat                │
│  │  │   └─ apply_tag                │  │  ←  ManyChat                │
│  │  │   ↓                           │  │                             │
│  │  │ Memory                        │  │                             │
│  │  └───────────────────────────────┘  │                             │
│  │             ↓                       │                             │
│  │  Formatter (splits into 1-6 msgs)   │                             │
│  │             ↓                       │                             │
│  │  Send Flow → ManyChat               │                             │
│  └─────────────────────────────────────┘                             │
│         │                                                            │
│         ▼                                                            │
│  ManyChat sends each split message to fan's IG inbox                 │
│  Fan replies, loop repeats, conversation memory persists             │
│                                                                      │
│  Tracking: attributable subs via dedicated UTM on OF link + ManyChat │
│  tag (`Subscribed`) cross-referenced with OF dashboard at month end. │
└──────────────────────────────────────────────────────────────────────┘

STAGE 3: V2 ON-PLATFORM (gated on V1 attribution proof + lawyer call)
┌──────────────────────────────────────────────────────────────────────┐
│  Chatter's browser on OnlyFans (paid sub is now chatting on OF)      │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────────────────────────────┐                             │
│  │  Chrome extension                   │                             │
│  │   • Reads active OF chat thread     │                             │
│  │   • POST to n8n webhook             │                             │
│  │   • Receives draft reply            │                             │
│  │   • Shows in side panel             │                             │
│  └─────────────────────────────────────┘                             │
│         │  POST /webhook/ofm-onplatform-<creator>                    │
│         ▼                                                            │
│  ┌─────────────────────────────────────┐                             │
│  │  n8n: Maya (Bella's on-platform     │                             │
│  │  sister, PPV-tuned)                 │                             │
│  │   ├─ PPV catalog                    │                             │
│  │   ├─ Sexting tier upsell            │                             │
│  │   ├─ Custom request close           │                             │
│  │   └─ Tip prompts                    │                             │
│  └─────────────────────────────────────┘                             │
│         │                                                            │
│         ▼                                                            │
│  Draft returned, chatter clicks "Insert" → "Send" in OF native UI    │
│  Human still presses send. No TOS violation. 3-5x chatter throughput │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Status by component

| Component | Status | Location / ID |
|-----------|--------|---------------|
| System prompt v1 (Bella) | ✅ Ready | `deliverables/system_prompt_v1.md` |
| Formatter prompt v1 | ✅ Ready | `deliverables/formatter_prompt_v1.md` |
| n8n production workflow template | ✅ Ready, placeholders need swap | `deliverables/n8n_workflow_ofm_v1.json` |
| ManyChat per-creator setup guide | ✅ Ready | `deliverables/manychat_setup_guide.md` |
| Per-creator KB template | ✅ Ready | `deliverables/creator_knowledge_base_template.md` |
| Mia test creator persona | ✅ Ready | `simulator/mia_test_creator.md` |
| Simulator workflow on n8n | ✅ Live | n8n id `35xDeYWpYVsCDU6L` |
| Simulator webhook | ✅ Live | https://n8n.ezjonline.com/webhook/ofm-sim-mia |
| chat.html test UI | ✅ Ready | `simulator/chat.html` |
| Python conversation runner | ✅ Ready | `simulator/run_simulation.py` |
| V2 on-platform plan | ✅ Documented | `v2_onplatform_options.md` |
| | | |
| Tom approval on Harvey | ❓ Pending | EZJ to ping Harvey |
| Pilot creator picked | ❓ Pending | Harvey to nominate |
| Per-creator Google Doc KB | ❓ Not built | Build per pilot creator |
| Pilot creator's ManyChat app | ❓ Not built | 60-90 min per the setup guide |
| Production n8n workflow cloned | ❓ Not deployed | Run a per-creator deploy script |
| Attribution mechanism | ❓ Not picked | Recommend ManyChat tag + manual reconciliation for V1 |
| Pricing finalized | ❓ Not run | Run `/hormozi pricing` |
| V2 Chrome extension | ❓ Not started | Gated on V1 proof + lawyer call |

---

## How to interact with the bot right now

**Option 1: Browser chat UI** (recommended for prompt iteration)

```
open /Users/Ethan/claudia/agency/products/ofm_ig_dm_agent/simulator/chat.html
```

10 quick-test buttons. Type freeform. Session persists across reloads. Reset button starts a fresh conversation. Copy button grabs the transcript.

**Option 2: Python scripted conversation runner** (for regression testing)

```bash
source venv/bin/activate
python3 agency/products/ofm_ig_dm_agent/simulator/run_simulation.py happy_path
# or: underage, ai_detection, explicit_request, broke, all
```

Logs save to `simulator/logs/<timestamp>_<scenario>_<id>.md`.

**Option 3: Direct curl** (debug / one-off)

```bash
curl -X POST https://n8n.ezjonline.com/webhook/ofm-sim-mia \
  -H "Content-Type: application/json" \
  -d '{"session_id":"my-session","message":"heyy"}'
```

Same session_id keeps memory; new session_id starts a fresh conversation.

---

## The narrowest path to first live IG conversation

Assuming Harvey says yes and picks a creator, the build sprint:

```
Day 1   Harvey green-lights + nominates pilot creator
Day 2   Build pilot creator's Google Doc knowledge base (creator fills voice samples)
Day 3   Clone n8n production workflow, rewire all <CREATOR_HANDLE> placeholders
Day 3   Generate per-creator ManyChat bearer token
Day 4   Per the setup guide: ManyChat custom fields, 4 trigger flows, Send Flow
Day 4   Swap simulator model from gpt-4o to Sonnet 4.6 if Anthropic creds get topped up
Day 5   End-to-end smoke test from a burner IG (or EZJ's IG)
Day 5   Patch any prompt issues found
Day 6   Creator reviews 10 sample conversations, approves voice + tone
Day 7   Flip live on the creator's real IG, EZJ monitors for 24 hours
Day 7+  Track attribution, iterate weekly
```

After day 7: case study capture starts. Day 14-30: $5+ attributable subs is the threshold for opening outbound to other OFMs.

---

## What I need from you to unlock the next stage

1. **Ping Harvey:** confirm Tom's status on the $700 form. If greenlit, ask Harvey to nominate a pilot creator.
2. **Top up Anthropic credits on one of the n8n creds** (or send me a fresh API key) so we can swap Bella from gpt-4o to Sonnet 4.6. Claude is more rule-adherent on the dash + markdown limits we saw slip in testing.
3. **Try the chat.html UI** — chat with Bella for 10 minutes, flag anything off-tone or off-brand. Prompt iteration is the cheapest improvement we can make right now.
