# OFM IG DM Agent

AI Instagram DM agent that converts an OF creator's followers into paying OF subs. Two-pronged business:

1. **Prong 1 — Bella-as-a-service:** install the bot in real OFM creators' IG DMs. Service biz, 15% rev share. Cash flow now. **Building Harvey pilot.**
2. **Prong 2 — We are the creator:** end-to-end AI-generated OF creators (visual + content + chat + growth). The moat. **Mia is persona #1, starting build in parallel.**

Strategy doc: [GTM_STRATEGY.md](GTM_STRATEGY.md) (both prongs).
Phase 2 build: [PHASE_2_AI_CREATORS.md](PHASE_2_AI_CREATORS.md) (the AI creator stack).

This is a working repo extracted from `ezjonline/claudia` as a standalone project so EZJ + Joe can collaborate without exposing the broader agency codebase.

## Status

V1 simulator is live. Bella (the agent) handles a full 6-phase conversion arc on the simulator with all 5 ManyChat tool calls firing into a mock workflow. Test her at the local chat UI (instructions below).

- [STATUS.md](STATUS.md) — architecture lifecycle map (sim → real OFM pilot → V2 on-platform → Phase 2 AI creators)
- [GTM_STRATEGY.md](GTM_STRATEGY.md) — two-prong business plan, unit economics, dashboard roadmap
- [PHASE_2_AI_CREATORS.md](PHASE_2_AI_CREATORS.md) — end-to-end AI creator stack
- [ATTRIBUTION.md](ATTRIBUTION.md) — how we prove Bella drove the sub (4-layer stack: Supabase + short link + OF promo + cross-ref)
- [COLLAB.md](COLLAB.md) — two-dev git workflow, sandbox isolation, branch protection
- [v2_onplatform_options.md](v2_onplatform_options.md) — Chrome extension chatter assistant analysis

## Quick start

```bash
git clone https://github.com/ezjonline/ofm-ig-dm-agent.git
cd ofm-ig-dm-agent
python3 -m venv venv
source venv/bin/activate
pip install requests python-dotenv
```

Create a `.env` file at the repo root:

```
N8N_BASE_URL=https://n8n.ezjonline.com
N8N_API_KEY=<from EZJ>
OPENAI_API_KEY=<from EZJ or your own>
ANTHROPIC_API_KEY=<from EZJ or your own>
OFM_SIM_OWNER=<your name, e.g. joe>
```

The `OFM_SIM_OWNER` value namespaces your n8n workflow sandbox so multiple developers don't overwrite each other. EZJ runs without it (default sandbox). Anyone else sets it to their initials/name.

## Deploy your sandbox

```bash
python3 simulator/deploy_full_simulator.py
```

Creates two n8n workflows tagged with your OWNER suffix:
- `OFM IG DM Agent SIMULATOR (Mia) V2 FULL [<OWNER>]`
- `OFM Mock ManyChat (SIM) [<OWNER>]`

And your webhook becomes `/webhook/ofm-sim-mia-v2-<owner>`.

## Test her

Start the local server:

```bash
cd simulator
python3 -m http.server 8080
```

Open `http://localhost:8080/chat.html?owner=<your-owner-name>` (or just `chat.html` if you're EZJ on the default sandbox).

Or run a scripted scenario:

```bash
python3 simulator/run_simulation.py happy_path
# scenarios: happy_path, vibe_test, underage, ai_detection, explicit_request, broke, all
```

Logs save to `simulator/logs/`.

## Project structure

```
.
├── README.md                    you are here
├── CLAUDE.md                    Tier 4 project context (loaded by Claude Code)
├── context.md                   ICP, offer, hard constraints
├── STATUS.md                    architecture lifecycle map (sim → Harvey pilot → V2)
├── GTM_STRATEGY.md              who we sell to, pricing, dashboard plan
├── COLLAB.md                    two-dev collaboration guide (read this first)
├── v2_onplatform_options.md     V2 on-platform chatter analysis
├── phases/                      execution playbook by phase
│   ├── README.md
│   ├── 01_adapt_workflow.md
│   ├── 02_harvey_pilot_deploy.md
│   ├── 03_pricing_and_offer.md
│   └── 04_productize_and_sell.md
├── deliverables/                production-ready assets
│   ├── system_prompt_v1.md      Bella's persona + phase flow (Joe's domain)
│   ├── formatter_prompt_v1.md   message-splitter prompt (deprecated post V2 refactor)
│   ├── n8n_workflow_ofm_v1.json production workflow template
│   ├── manychat_setup_guide.md  60-90 min per-creator setup checklist
│   ├── creator_knowledge_base_template.md
│   ├── source_joe_auramax_workflow.json     untouched reference
│   └── source_joe_auramax_system_prompt.md  untouched reference
└── simulator/
    ├── deploy_full_simulator.py  builds + pushes the n8n workflow
    ├── run_simulation.py         scripted conversation tester
    ├── chat.html                 browser test UI (IG-style bubbles)
    ├── mia_test_creator.md       Mia synthetic creator persona
    └── logs/                     test transcripts (gitignored)
```

## Working with Joe

See [COLLAB.md](COLLAB.md) for the full multi-developer setup. TL;DR:

1. Get added as a Write collaborator on this repo
2. Clone, set up `.env` with your `OFM_SIM_OWNER`
3. Work on feature branches, open PRs, merge to main
4. Both devs' sandbox workflows live side by side on the shared n8n

Suggested ownership split:
- **Joe** owns voice / persona / flirt cadence (`deliverables/system_prompt_v1.md`, `simulator/mia_test_creator.md`)
- **EZJ** owns infra / deploy / production rollout (`simulator/`, `deliverables/n8n_workflow_ofm_v1.json`)

## What's not in this repo (intentionally)

- API credentials (live in your own `.env` or `~/.claude-secrets/`)
- The broader `ezjonline/claudia` agency codebase (Google Ads, Stripe, other clients)
- Per-creator production deployments (each creator gets their own n8n workflow + ManyChat app; this repo is the template)
