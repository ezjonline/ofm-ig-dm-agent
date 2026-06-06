# How EZJ + Joe collaborate on this project

Two developers, same project, no stepping on each other. Standard git flow with one twist: per-dev sandbox workflows on the shared n8n instance.

This is a **standalone repo** at `ezjonline/ofm-ig-dm-agent`. Joe only gets access to this repo, not to EZJ's broader agency codebase. Different repo means different access control.

---

## One-time setup (per developer)

### EZJ (already done)
- Repo at `https://github.com/ezjonline/ofm-ig-dm-agent`
- Local checkout at `~/ofm-ig-dm-agent/` (separate from `~/claudia/`)
- Secrets live at `~/.claude-secrets/claudia/.env` (legacy) OR `<repo>/.env` OR `~/.claude-secrets/ofm-ig-dm-agent/.env` (recommended for new setups). The deploy script checks all three.
- Default sandbox = no suffix → `/webhook/ofm-sim-mia-v2`

### Joe (first-time setup)

1. **Get added to the GitHub repo.** EZJ runs from his terminal:
   ```bash
   gh repo invite ezjonline/ofm-ig-dm-agent <joe-github-username> --permission write
   ```
   Or via UI: https://github.com/ezjonline/ofm-ig-dm-agent/settings/access → Add people → Joe's username → role: **Write**. Joe accepts via email.

2. **Clone + install:**
   ```bash
   git clone https://github.com/ezjonline/ofm-ig-dm-agent.git
   cd ofm-ig-dm-agent
   python3 -m venv venv
   source venv/bin/activate
   pip install requests python-dotenv
   ```

3. **Set up secrets.** Easiest: drop a `.env` file at the repo root (gitignored automatically). EZJ shares values via 1Password / DM:
   ```
   N8N_BASE_URL=https://n8n.ezjonline.com
   N8N_API_KEY=<from EZJ>
   ANTHROPIC_API_KEY=<from EZJ or his own>
   OPENAI_API_KEY=<from EZJ or his own>
   OFM_SIM_OWNER=joe
   ```
   The last line is the critical part. It namespaces all his n8n workflows and webhooks so he's never overwriting EZJ's.

4. **Install Claude Code** (https://docs.claude.com/claude-code). Joe opens it pointed at his cloned `ofm-ig-dm-agent` directory. His Claude Code only sees this project, nothing else of EZJ's.

5. **Deploy his own sandbox:**
   ```bash
   source venv/bin/activate
   python3 simulator/deploy_full_simulator.py
   ```
   This creates two new n8n workflows tagged `[JOE]`:
   - `OFM IG DM Agent SIMULATOR (Mia) V2 FULL [JOE]`
   - `OFM Mock ManyChat (SIM) [JOE]`

   And his webhook becomes `/webhook/ofm-sim-mia-v2-joe`. EZJ's stays untouched.

6. **Chat with his Bella:**
   ```bash
   cd simulator
   python3 -m http.server 8080
   ```
   Then open `http://localhost:8080/chat.html?owner=joe`. The `?owner=joe` URL param points chat.html at his sandbox.

---

## Daily workflow (both of you)

### When you start working

```bash
git pull origin main
```
Grab whatever the other person merged since last time.

### When you're ready to make changes

Create a branch for your work so the other person isn't blocked while you iterate:

```bash
# Joe iterates on the voice
git checkout -b joe/voice-iteration-flirt-tones

# EZJ builds the attribution dashboard
git checkout -b ezj/attribution-dashboard
```

Edit, test, redeploy your sandbox, iterate. As many times as you want. Your branch is yours.

### When you're ready to share

```bash
git add -A
git commit -m "voice: tighten the flirt cadence on phase 2 reactions"
git push -u origin joe/voice-iteration-flirt-tones
```

Then open a Pull Request on GitHub (or use the `gh` CLI: `gh pr create`). The other person reviews, comments, merges. Once merged to main, both of you `git pull origin main` and you're synced.

### When you want EZJ's prompt changes applied to your sandbox

After pulling main:

```bash
python3 agency/products/ofm_ig_dm_agent/simulator/deploy_full_simulator.py
```

Your sandbox gets the latest prompt. EZJ's sandbox is also already on the latest (he ran it after his merge).

---

## Who owns what (suggested split)

| Owner | Files / scope |
|-------|---------------|
| **Joe** | `deliverables/system_prompt_v1.md` (Bella's voice + persona + flirt cadence) |
| **Joe** | `simulator/mia_test_creator.md` (Mia's KB + voice samples) |
| **Joe** | `deliverables/formatter_prompt_v1.md` (if we re-introduce a formatter LLM step) |
| **EZJ** | `simulator/deploy_full_simulator.py` (n8n workflow shape) |
| **EZJ** | `simulator/chat.html` (test UI) |
| **EZJ** | `simulator/run_simulation.py` (regression scenarios) |
| **EZJ** | `deliverables/n8n_workflow_ofm_v1.json` (production template) |
| **EZJ** | `deliverables/manychat_setup_guide.md` (deployment infra) |
| **EZJ** | `GTM_STRATEGY.md`, `STATUS.md` (business strategy) |
| **Both** | `CLAUDE.md`, `context.md` (project docs) |
| **Both** | `simulator/logs/` (test transcripts, can both add) |

Not a hard rule. If Joe wants to fix a deploy script bug or EZJ wants to tweak a voice rule, just do it. The split is about default ownership, not enforcement.

---

## n8n workflow namespace

| Workflow | EZJ's name | Joe's name |
|----------|-----------|-----------|
| OFM simulator | `OFM IG DM Agent SIMULATOR (Mia) V2 FULL` | `OFM IG DM Agent SIMULATOR (Mia) V2 FULL [JOE]` |
| Mock ManyChat | `OFM Mock ManyChat (SIM)` | `OFM Mock ManyChat (SIM) [JOE]` |
| Webhook | `/webhook/ofm-sim-mia-v2` | `/webhook/ofm-sim-mia-v2-joe` |
| Mock setCustomFields | `/webhook/mock-mc-setCustomFields` | `/webhook/mock-mc-setCustomFields-joe` |
| Mock addTagByName | `/webhook/mock-mc-addTagByName` | `/webhook/mock-mc-addTagByName-joe` |

Both live on `n8n.ezjonline.com`. The `OFM_SIM_OWNER` env var drives the suffix automatically.

---

## When you DON'T want to use branches (small changes)

For a 1-line typo fix in a doc, just commit straight to main:
```bash
git pull origin main
# edit
git add -A && git commit -m "typo fix" && git push origin main
```

For anything bigger (prompt rewrites, new tools, refactor) → use a branch + PR. Protects both of you from "wait you overwrote my change."

---

## What about merge conflicts on `system_prompt_v1.md`?

If you both edit the system prompt at the same time, git will flag conflicts. To minimize this:

1. **Talk before big rewrites.** Drop a line in your shared chat (Telegram / Discord) saying "yo I'm about to rewrite the Phase 4 section, hands off for an hour."
2. **Pull frequently.** Before starting a session: `git pull origin main`. After a long session before pushing: `git pull origin main --rebase`.
3. **Smaller commits.** A prompt change to "tone down emoji frequency" is one commit. "Rewrite all of Phase 2" is one commit. Don't bundle 5 unrelated edits.

If you do conflict, git tells you which sections are conflicting. Open the file, the conflict markers (`<<<<<<<` / `=======` / `>>>>>>>`) show both versions. Pick the one you want (or merge both manually), delete the markers, commit.

---

## Quick reference

```bash
# Daily start
git pull origin main

# Start a feature
git checkout -b yourname/what-youre-doing

# Save progress
git add -A && git commit -m "what changed"
git push -u origin yourname/what-youre-doing

# Open PR
gh pr create

# Get latest from main during a feature
git pull origin main --rebase

# Done with feature, after PR merged
git checkout main
git pull origin main
git branch -d yourname/what-youre-doing
```

---

## What about Claude Code working on the same files simultaneously?

You both run separate Claude Code instances on your own machines. Each Claude only sees the files on its own developer's machine. They never directly talk to each other.

Coordination happens through git (commits, PRs). If Joe's Claude edits `system_prompt_v1.md` and EZJ's Claude edits the same file at the same time, the second person to push will get a merge conflict and resolve it.

This is exactly how every multi-dev team works. Git is the coordination layer.

The thing to avoid: don't both deploy to the same sandbox at the same time. That's what `OFM_SIM_OWNER` is for. Each Claude deploys to its own sandbox.

---

## Production deploy (later, when we go live with Harvey)

The simulator sandboxes are for iteration. When we deploy to Harvey's actual creator's IG via ManyChat, that's a third workflow: `OFM IG DM Agent PRODUCTION (<creator-handle>)`. We'll use `OFM_SIM_OWNER=prod` or a separate `deploy_production.py` script. Joe and EZJ both have access; one person at a time runs the production deploy.
