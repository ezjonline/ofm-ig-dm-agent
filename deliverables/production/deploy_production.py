#!/usr/bin/env python3
"""
Deploy the PRODUCTION OFM IG DM Agent (Bella) to n8n.ezjonline.com.

This is the real, ManyChat-connected version of the validated simulator. It
reuses the exact node shape we hardened in simulator/deploy_full_simulator.py
(Bella brain, 5 OFM tool calls, blank-line bubble split, no second formatter
LLM hop) and rewires it from the Mock ManyChat sandbox to the real ManyChat
API, plus a per-creator Google Docs knowledge base, on Claude Sonnet 4.6.

What changes vs the simulator:
  - Tool calls POST to https://api.manychat.com (Bearer auth) instead of the
    Mock ManyChat webhooks. Credential: per-creator httpBearerAuth.
  - subscriber_id comes from the ManyChat webhook body.id, not a session_id.
  - Knowledge base is a Google Docs tool (per-creator doc), not inlined.
  - Primary model is Sonnet 4.6, fallback Haiku 4.5 (both Anthropic).
  - System prompt is the production Bella prompt (deliverables/system_prompt_v1.md),
    which already carries the ManyChat dynamic-context prefix.

It is NON-DESTRUCTIVE: it creates a new workflow and never touches the live
"EZJ IG DM Setter" (Qa6mkmkvFIgargSt, EZJ's agency lead-gen) or the simulator.
The new workflow is created INACTIVE. Activate it in the n8n UI only after the
per-creator ManyChat credential, External Request, and KB doc are wired (see
deliverables/manychat_setup_guide.md).

Per-creator config via env (defaults target the Mia test on EZJ's ManyChat):
  OFM_CREATOR_SLUG    webhook path slug         (default: mia)
  OFM_CREATOR_NAME    creator first name        (default: Mia)
  OFM_CREATOR_HANDLE  creator IG handle         (default: mia.everyday)
  OFM_MANYCHAT_CRED_ID / _NAME   httpBearerAuth cred for the creator's ManyChat
  OFM_KB_DOC_URL      Google Doc URL of the creator's knowledge base

Run:
    python3 deliverables/production/deploy_production.py
"""
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]

for _env_path in [
    REPO_ROOT / ".env",
    Path.home() / ".claude-secrets" / "ofm-ig-dm-agent" / ".env",
    Path.home() / ".claude-secrets" / "claudia" / ".env",
]:
    if _env_path.exists():
        load_dotenv(_env_path)
        break

N8N_BASE_URL = os.environ.get("N8N_BASE_URL", "https://n8n.ezjonline.com").rstrip("/")
N8N_API_KEY = os.environ["N8N_API_KEY"]
HEADERS = {"X-N8N-API-KEY": N8N_API_KEY, "Content-Type": "application/json"}

# Anthropic credential (live, credit topped up 2026-06-13).
ANTHROPIC_CRED_ID = "WMwxvyJGynY7n2aB"
ANTHROPIC_CRED_NAME = "Anthropic v3"

# ManyChat Bearer credential. Default is EZJ's own ManyChat token, which is the
# correct target for the Mia burner test (we reuse his existing account, no new
# seat). Swap per creator at onboarding.
MANYCHAT_CRED_ID = os.environ.get("OFM_MANYCHAT_CRED_ID", "BEBNzwltw3uNqNns")
MANYCHAT_CRED_NAME = os.environ.get("OFM_MANYCHAT_CRED_NAME", "EZJ ManyChat API")

# Per-creator knowledge base Google Doc. PLACEHOLDER until the creator's KB doc
# exists. The workflow ships inactive, so an empty/placeholder URL is fine until
# onboarding fills it.
KB_DOC_URL = os.environ.get("OFM_KB_DOC_URL", "PLACEHOLDER_SET_CREATOR_KB_DOC_URL")

CREATOR_SLUG = os.environ.get("OFM_CREATOR_SLUG", "mia").strip().lower()
CREATOR_NAME = os.environ.get("OFM_CREATOR_NAME", "Mia")
CREATOR_HANDLE = os.environ.get("OFM_CREATOR_HANDLE", "mia.everyday")

WF_NAME = f"OFM IG DM Agent PRODUCTION (Bella x {CREATOR_NAME})"
WEBHOOK_PATH = f"ofm-prod-{CREATOR_SLUG}"

SYSTEM_PROMPT_FILE = REPO_ROOT / "deliverables" / "system_prompt_v1.md"

MC_SETFIELDS_URL = "https://api.manychat.com/fb/subscriber/setCustomFields"
MC_ADDTAG_URL = "https://api.manychat.com/fb/subscriber/addTagByName"


# --- n8n API helpers ---------------------------------------------------------

def find_workflow_id(name: str):
    cursor = None
    while True:
        params = "?limit=250" + (f"&cursor={cursor}" if cursor else "")
        r = requests.get(f"{N8N_BASE_URL}/api/v1/workflows{params}", headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
        for w in data.get("data", []):
            if w["name"] == name:
                return w["id"]
        cursor = data.get("nextCursor")
        if not cursor:
            return None


def deactivate(wf_id):
    requests.post(f"{N8N_BASE_URL}/api/v1/workflows/{wf_id}/deactivate", headers=HEADERS, timeout=30)


def delete_wf(wf_id):
    requests.delete(f"{N8N_BASE_URL}/api/v1/workflows/{wf_id}", headers=HEADERS, timeout=30)


def create_wf(wf):
    r = requests.post(f"{N8N_BASE_URL}/api/v1/workflows", headers=HEADERS, data=json.dumps(wf), timeout=60)
    if r.status_code not in (200, 201):
        sys.exit(f"[error] create failed: {r.status_code}\n{r.text[:2000]}")
    return r.json()["id"]


# --- prompt loader -----------------------------------------------------------

def load_production_system_message() -> str:
    """Build the AI Agent systemMessage from the production Bella prompt.

    The prompt file holds the ManyChat dynamic-context prefix inside the first
    fenced block, then the static body after the first '---'. We stitch them
    into a single n8n expression string and bake the creator's name/handle.
    """
    text = SYSTEM_PROMPT_FILE.read_text()
    parts = text.split("```")
    if len(parts) < 3:
        sys.exit("system_prompt_v1.md: could not find fenced dynamic-prefix block")
    prefix = parts[1].strip()
    body = text.split("---", 1)[1].strip()
    msg = prefix + "\n\n" + body
    msg = (msg.replace("[CREATOR_NAME]", CREATOR_NAME)
              .replace("[creator first name]", CREATOR_NAME)
              .replace("[CREATOR_HANDLE]", CREATOR_HANDLE))
    if not msg.startswith("="):
        msg = "=" + msg
    return msg


# --- node builders -----------------------------------------------------------

def mc_setfields_tool(name, node_id, description, fields_json, y):
    return {
        "parameters": {
            "toolDescription": description,
            "method": "POST",
            "url": MC_SETFIELDS_URL,
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "httpBearerAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": fields_json,
            "options": {},
        },
        "type": "n8n-nodes-base.httpRequestTool",
        "typeVersion": 4.3,
        "position": [600, y],
        "id": node_id,
        "name": name,
        "credentials": {"httpBearerAuth": {"id": MANYCHAT_CRED_ID, "name": MANYCHAT_CRED_NAME}},
    }


# subscriber_id sourced from the ManyChat webhook body.id (real ManyChat id).
SID = "{{ $('Webhook').item.json.body.id }}"


def build_workflow() -> dict:
    system_msg = load_production_system_message()

    nodes = [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": WEBHOOK_PATH,
                "responseMode": "responseNode",
                "options": {},
            },
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2.1,
            "position": [200, 300],
            "id": "ofm-webhook",
            "name": "Webhook",
            "webhookId": WEBHOOK_PATH,
        },
        {
            "parameters": {
                "promptType": "define",
                # ManyChat posts the full ContactJson; the fan's latest message
                # lives in the custom field the trigger flow sets. Fallbacks keep
                # the simulator's flat {message} shape working too.
                "text": "={{ $json.body.custom_fields[\"AI > User Messages\"] || $json.body.last_input_text || $json.body.message }}",
                "needsFallback": True,
                "options": {"systemMessage": system_msg, "maxIterations": 10},
            },
            "type": "@n8n/n8n-nodes-langchain.agent",
            "typeVersion": 3,
            "position": [500, 300],
            "id": "ofm-agent",
            "name": "AI Agent",
            "retryOnFail": True,
            "waitBetweenTries": 3000,
            "maxTries": 2,
        },
        # Primary model: Sonnet 4.6.
        {
            "parameters": {
                "model": {"__rl": True, "value": "claude-sonnet-4-6", "mode": "list", "cachedResultName": "Claude Sonnet 4.6"},
                "options": {"maxTokensToSample": 2000, "temperature": 0.9},
            },
            "type": "@n8n/n8n-nodes-langchain.lmChatAnthropic",
            "typeVersion": 1.3,
            "position": [380, 520],
            "id": "ofm-model",
            "name": "AI Model",
            "credentials": {"anthropicApi": {"id": ANTHROPIC_CRED_ID, "name": ANTHROPIC_CRED_NAME}},
        },
        # Fallback model: Haiku 4.5 (cheap, keeps her alive if Sonnet errors).
        {
            "parameters": {
                "model": {"__rl": True, "value": "claude-haiku-4-5-20251001", "mode": "list", "cachedResultName": "Claude Haiku 4.5"},
                "options": {"maxTokensToSample": 2000, "temperature": 0.9},
            },
            "type": "@n8n/n8n-nodes-langchain.lmChatAnthropic",
            "typeVersion": 1.3,
            "position": [500, 520],
            "id": "ofm-model-fallback",
            "name": "AI Model Fallback",
            "credentials": {"anthropicApi": {"id": ANTHROPIC_CRED_ID, "name": ANTHROPIC_CRED_NAME}},
        },
        {
            "parameters": {
                "sessionIdType": "customKey",
                "sessionKey": "={{ $json.body.id }}",
                "contextWindowLength": 30,
            },
            "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
            "typeVersion": 1.3,
            "position": [620, 520],
            "id": "ofm-memory",
            "name": "Memory",
        },
        # Per-creator knowledge base (Google Doc). Swap documentURL per creator.
        {
            "parameters": {"operation": "get", "documentURL": KB_DOC_URL},
            "type": "n8n-nodes-base.googleDocsTool",
            "typeVersion": 2,
            "position": [740, 520],
            "id": "ofm-kb",
            "name": "Knowledge base",
        },
        # The 5 OFM tool calls (real ManyChat, Bearer auth).
        mc_setfields_tool(
            "save_qualification_data", "tool-qual",
            "Fire ONCE at end of Phase 0 when both 18+ confirmed AND country known. Pass country, age, qualified.",
            '={\n  "subscriber_id": "' + SID + '",\n  "fields": [\n    {"field_name": "country", "field_value": "{{ $fromAI(\'country\', \'Country text\', \'string\') }}"},\n    {"field_name": "age", "field_value": "{{ $fromAI(\'age\', \'Age integer 18+\', \'number\') }}"},\n    {"field_name": "qualified", "field_value": "{{ $fromAI(\'qualified\', \'true or false\', \'string\') }}"}\n  ]\n}',
            700,
        ),
        mc_setfields_tool(
            "save_discovery_data", "tool-disc",
            "Fire ONCE at end of Phase 2 before Phase 3 tease. Pass vibe, interests, why_followed, urgency_to_sub, mention_of_other_creators.",
            '={\n  "subscriber_id": "' + SID + '",\n  "fields": [\n    {"field_name": "vibe", "field_value": "{{ $fromAI(\'vibe\', \'Fans energy\', \'string\') }}"},\n    {"field_name": "interests", "field_value": "{{ $fromAI(\'interests\', \'Content style\', \'string\') }}"},\n    {"field_name": "why_followed", "field_value": "{{ $fromAI(\'whyFollowed\', \'How they found her\', \'string\') }}"},\n    {"field_name": "urgency_to_sub", "field_value": "{{ $fromAI(\'urgencyToSub\', \'High Medium Low\', \'string\') }}"},\n    {"field_name": "mention_of_other_creators", "field_value": "{{ $fromAI(\'mentionOfOtherCreators\', \'Mentioned other creators\', \'string\') }}"}\n  ]\n}',
            800,
        ),
        mc_setfields_tool(
            "save_subscription_data", "tool-sub",
            "Fire ONCE in Phase 5 only after fan explicitly confirms they subscribed. Pass subbed, sub_tier, subbed_timestamp.",
            '={\n  "subscriber_id": "' + SID + '",\n  "fields": [\n    {"field_name": "subbed", "field_value": "{{ $fromAI(\'subbed\', \'true or false\', \'string\') }}"},\n    {"field_name": "sub_tier", "field_value": "{{ $fromAI(\'subTier\', \'Tier text\', \'string\') }}"},\n    {"field_name": "subbed_timestamp", "field_value": "{{ $fromAI(\'subbedTimestamp\', \'ISO datetime\', \'string\') }}"}\n  ]\n}',
            900,
        ),
        mc_setfields_tool(
            "update_conversation_state", "tool-state",
            "Fire on every phase transition and mid-phase in 2-4. Pass current_phase (0-5) and conversation_summary (under 200 words).",
            '={\n  "subscriber_id": "' + SID + '",\n  "fields": [\n    {"field_name": "current_phase", "field_value": "{{ $fromAI(\'currentPhase\', \'0-5\', \'number\') }}"},\n    {"field_name": "conversation_summary", "field_value": "{{ $fromAI(\'conversationSummary\', \'Under 200 words\', \'string\') }}"}\n  ]\n}',
            1000,
        ),
        {
            "parameters": {
                "toolDescription": "Fire when a milestone is hit. Use exactly one of: Trust_Asset_Sent, OF_Link_Pitched, Subscribed, AI_Detection_Triggered, Disqualified_Lead, Human_Alert_Check_Prospect.",
                "method": "POST",
                "url": MC_ADDTAG_URL,
                "authentication": "predefinedCredentialType",
                "nodeCredentialType": "httpBearerAuth",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": '={\n  "subscriber_id": "' + SID + '",\n  "tag_name": "{{ $fromAI(\'tagName\', \'One of the 6 approved tags\', \'string\') }}"\n}',
                "options": {},
            },
            "type": "n8n-nodes-base.httpRequestTool",
            "typeVersion": 4.3,
            "position": [600, 1100],
            "id": "tool-tag",
            "name": "apply_tag",
            "credentials": {"httpBearerAuth": {"id": MANYCHAT_CRED_ID, "name": MANYCHAT_CRED_NAME}},
        },
        # Deterministic blank-line bubble split (no second LLM hop).
        {
            "parameters": {
                "jsCode": (
                    "let raw = $('AI Agent').first().json.output || '';\n"
                    "let text = typeof raw === 'string' ? raw : (raw.output || JSON.stringify(raw));\n"
                    "text = text.replace(/\\[Used tools?: [^\\]]*?\\]\\s*/gs, '');\n"
                    "text = text.replace(/^\\s+/, '').replace(/\\s+$/, '');\n"
                    "let parts = text.split(/\\n\\s*\\n+/).map(s => s.trim()).filter(Boolean);\n"
                    "if (!parts.length) parts = [text.trim()];\n"
                    "if (parts.length > 6) {\n"
                    "  const tail = parts.slice(5).join('\\n\\n');\n"
                    "  parts = parts.slice(0, 5).concat([tail]);\n"
                    "}\n"
                    "const fields = parts.map((value, i) => ({ field_name: 'AI > Answer ' + (i + 1), field_value: value }));\n"
                    "return [{ json: {\n"
                    "  subscriber_id: $('Webhook').first().json.body.id,\n"
                    "  fields,\n"
                    "  texts: parts,\n"
                    "  combined: parts.join('\\n\\n'),\n"
                    "} }];"
                ),
            },
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [800, 300],
            "id": "ofm-code",
            "name": "Split into messages",
        },
        # Write the split bubbles to ManyChat custom fields (AI > Answer 1..6).
        {
            "parameters": {
                "method": "POST",
                "url": MC_SETFIELDS_URL,
                "authentication": "predefinedCredentialType",
                "nodeCredentialType": "httpBearerAuth",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({ subscriber_id: $json.subscriber_id, fields: $json.fields }) }}",
                "options": {},
            },
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.3,
            "position": [1000, 300],
            "id": "ofm-set-answers",
            "name": "Set AI Answers",
            "credentials": {"httpBearerAuth": {"id": MANYCHAT_CRED_ID, "name": MANYCHAT_CRED_NAME}},
        },
        {
            "parameters": {
                "respondWith": "json",
                "responseBody": "={{ JSON.stringify({ messages: $('Split into messages').first().json.texts, combined: $('Split into messages').first().json.combined }) }}",
                "options": {},
            },
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1.1,
            "position": [1200, 300],
            "id": "ofm-respond",
            "name": "Respond to Webhook",
        },
    ]

    connections = {
        "Webhook": {"main": [[{"node": "AI Agent", "type": "main", "index": 0}]]},
        "AI Agent": {"main": [[{"node": "Split into messages", "type": "main", "index": 0}]]},
        "Split into messages": {"main": [[{"node": "Set AI Answers", "type": "main", "index": 0}]]},
        "Set AI Answers": {"main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]},
        "AI Model": {"ai_languageModel": [[{"node": "AI Agent", "type": "ai_languageModel", "index": 0}]]},
        "AI Model Fallback": {"ai_languageModel": [[{"node": "AI Agent", "type": "ai_languageModel", "index": 1}]]},
        "Memory": {"ai_memory": [[{"node": "AI Agent", "type": "ai_memory", "index": 0}]]},
        "Knowledge base": {"ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]},
        "save_qualification_data": {"ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]},
        "save_discovery_data": {"ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]},
        "save_subscription_data": {"ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]},
        "update_conversation_state": {"ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]},
        "apply_tag": {"ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]},
    }

    return {
        "name": WF_NAME,
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"},
    }


def main():
    wf = build_workflow()

    # Save a local snapshot for review/diffing.
    out = Path(__file__).resolve().parent / "production_workflow.json"
    out.write_text(json.dumps(wf, indent=2))
    print(f"[ok] workflow JSON saved: {out}")

    existing = find_workflow_id(WF_NAME)
    if existing:
        print(f"[info] existing production workflow {existing}; deactivate + delete + recreate")
        deactivate(existing)
        delete_wf(existing)

    wf_id = create_wf(wf)
    print(f"[ok] PRODUCTION workflow created INACTIVE: id={wf_id}")
    print(f"     {N8N_BASE_URL}/workflow/{wf_id}")
    print(f"     webhook (inactive until activated): {N8N_BASE_URL}/webhook/{WEBHOOK_PATH}")
    print()
    print("Before activating in the n8n UI, confirm per-creator wiring:")
    print(f"  - ManyChat Bearer cred: {MANYCHAT_CRED_NAME} ({MANYCHAT_CRED_ID})")
    print(f"  - KB Google Doc URL: {KB_DOC_URL}")
    if KB_DOC_URL.startswith("PLACEHOLDER"):
        print("    ^ still a placeholder. Set OFM_KB_DOC_URL to the creator's KB doc and redeploy.")
    print(f"  - Creator: {CREATOR_NAME} (@{CREATOR_HANDLE}), webhook slug '{CREATOR_SLUG}'")
    print("  - ManyChat External Request must POST { id, first_name, ig_username, message, custom_fields } to the webhook.")
    print("  - See deliverables/manychat_setup_guide.md")


if __name__ == "__main__":
    main()
