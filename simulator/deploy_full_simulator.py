#!/usr/bin/env python3
"""
Deploy the FULL-SHAPE OFM IG DM Agent simulator to n8n.ezjonline.com.

This mirrors Joe's AuraMax workflow architecture node-for-node:

    Webhook
       v
    AI Agent  +-- AI Model (gpt-4o)
       +-- AI Model Fallback (gpt-4o-mini)
       +-- Memory (session-keyed window)
       +-- Knowledge base (Mia inlined in system prompt)
       +-- save_qualification_data  --> Mock ManyChat /setCustomFields
       +-- save_discovery_data      --> Mock ManyChat /setCustomFields
       +-- save_subscription_data   --> Mock ManyChat /setCustomFields
       +-- update_conversation_state --> Mock ManyChat /setCustomFields
       +-- apply_tag                 --> Mock ManyChat /addTagByName
       v
    Message a model (formatter, splits to AI > Answer 1..6)
       v
    Code in JavaScript (formats into ManyChat-style fields array)
       v
    Set AI Answers (POST Mock ManyChat /setCustomFields)
       v
    Respond to Webhook (returns the split messages array to chat.html)

Also deploys a 'Mock ManyChat' workflow with 3 webhook endpoints
(/mock-mc-setCustomFields, /mock-mc-addTagByName, /mock-mc-sendFlow)
that just return success so the tool calls in the OFM workflow always
succeed. This lets us test the production-shape architecture end to
end without a real ManyChat token.

Run:
    python3 agency/products/ofm_ig_dm_agent/simulator/deploy_full_simulator.py
"""
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# Standalone repo layout: simulator/ is one level under repo root.
REPO_ROOT = Path(__file__).resolve().parents[1]

# Load env from:
# 1. Local .env at repo root (preferred, per-dev override)
# 2. ~/.claude-secrets/ofm-ig-dm-agent/.env (recommended for shared secrets)
# 3. ~/.claude-secrets/claudia/.env (legacy fallback, EZJ's existing setup)
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

OPENAI_CRED_ID = "ZmA2gnjYXr7QhKQw"
OPENAI_CRED_NAME = "YouTube Research Agent - OpenAi"

SIM_DIR = REPO_ROOT / "simulator"
SYSTEM_PROMPT_FILE = REPO_ROOT / "deliverables" / "system_prompt_v1.md"
FORMATTER_PROMPT_FILE = REPO_ROOT / "deliverables" / "formatter_prompt_v1.md"
MIA_PERSONA_FILE = SIM_DIR / "mia_test_creator.md"

# Per-developer workflow isolation.
# Set OFM_SIM_OWNER in your env to deploy a sandbox that doesn't clobber
# anyone else's. Examples:
#   EZJ runs:        (unset, default)        -> /webhook/ofm-sim-mia-v2
#   Joe runs:        OFM_SIM_OWNER=joe       -> /webhook/ofm-sim-mia-v2-joe
#   Anyone CI/test:  OFM_SIM_OWNER=ci        -> /webhook/ofm-sim-mia-v2-ci
# Each dev's chat.html and run_simulation.py auto-pick up the right
# webhook because they read OFM_SIM_OWNER too (see below).
_OWNER = os.environ.get("OFM_SIM_OWNER", "").strip().lower()
_SUFFIX = f"-{_OWNER}" if _OWNER else ""
_NAME_SUFFIX = f" [{_OWNER.upper()}]" if _OWNER else ""

MOCK_MC_NAME = f"OFM Mock ManyChat (SIM){_NAME_SUFFIX}"
OFM_NAME = f"OFM IG DM Agent SIMULATOR (Mia) V2 FULL{_NAME_SUFFIX}"

OFM_WEBHOOK_PATH = f"ofm-sim-mia-v2{_SUFFIX}"
MOCK_SET_FIELDS_PATH = f"mock-mc-setCustomFields{_SUFFIX}"
MOCK_ADD_TAG_PATH = f"mock-mc-addTagByName{_SUFFIX}"
MOCK_SEND_FLOW_PATH = f"mock-mc-sendFlow{_SUFFIX}"


def load_prompt_body() -> str:
    text = SYSTEM_PROMPT_FILE.read_text()
    parts = text.split("---", 1)
    if len(parts) < 2:
        sys.exit("system_prompt_v1.md missing --- separator")
    return parts[1].strip()


def load_formatter_body() -> str:
    text = FORMATTER_PROMPT_FILE.read_text()
    # Extract the fenced code block (the actual prompt)
    if "```" in text:
        body = text.split("```", 2)[1]
        # strip optional language line
        if body.startswith("\n"):
            body = body[1:]
        return body.strip()
    return text.strip()


def baked_system_message() -> str:
    prompt_body = load_prompt_body().replace("[CREATOR_NAME]", "Mia").replace("[creator first name]", "Mia").replace("[CREATOR_HANDLE]", "mia.everyday")
    mia = MIA_PERSONA_FILE.read_text()
    header = (
        "# SIMULATOR V2 MODE (FULL ARCHITECTURE)\n\n"
        "You are running in a full-architecture simulator that mirrors the production "
        "Joe-pattern workflow node-for-node. ManyChat is replaced by a Mock ManyChat "
        "workflow inside the same n8n. All 5 tool calls (save_qualification_data, "
        "save_discovery_data, save_subscription_data, update_conversation_state, "
        "apply_tag) DO work and DO fire. Call them at the correct phase transitions "
        "exactly as the production prompt instructs. The mock receives the payloads and "
        "returns success.\n\n"
        "The knowledge_base tool is not wired in this simulator; instead Mia's full "
        "knowledge base is inlined below. Treat the section titled 'MIA - KNOWLEDGE BASE "
        "(INLINED)' as the authoritative source for any Mia-specific question.\n\n"
        "Other than that, behave exactly as the production prompt instructs.\n\n---\n\n"
    )
    kb = "# MIA - KNOWLEDGE BASE (INLINED)\n\n" + mia + "\n\n---\n\n"
    return header + kb + prompt_body


def find_workflow_id(name: str) -> str | None:
    """Find a workflow by exact name, paginating across all workflows.

    The n8n API returns ~100 workflows per page by default. EZJ's instance
    has 150+ workflows, so a single GET misses the OFM ones and the deploy
    script ends up creating duplicates on every run. Paginate by cursor.
    """
    cursor = None
    while True:
        params = "?limit=250"
        if cursor:
            params += f"&cursor={cursor}"
        r = requests.get(f"{N8N_BASE_URL}/api/v1/workflows{params}", headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
        for w in data.get("data", []):
            if w["name"] == name:
                return w["id"]
        cursor = data.get("nextCursor")
        if not cursor:
            return None


def deactivate(wf_id: str):
    requests.post(f"{N8N_BASE_URL}/api/v1/workflows/{wf_id}/deactivate", headers=HEADERS, timeout=30)


def delete_wf(wf_id: str):
    requests.delete(f"{N8N_BASE_URL}/api/v1/workflows/{wf_id}", headers=HEADERS, timeout=30)


def create_wf(wf: dict) -> str:
    r = requests.post(f"{N8N_BASE_URL}/api/v1/workflows", headers=HEADERS, data=json.dumps(wf), timeout=60)
    if r.status_code not in (200, 201):
        print(f"[error] create failed: {r.status_code}\n{r.text[:2000]}")
        sys.exit(1)
    return r.json()["id"]


def activate(wf_id: str):
    r = requests.post(f"{N8N_BASE_URL}/api/v1/workflows/{wf_id}/activate", headers=HEADERS, timeout=30)
    if r.status_code != 200:
        print(f"[error] activate failed: {r.status_code}\n{r.text[:500]}")
        sys.exit(1)


def build_mock_manychat() -> dict:
    """3 webhook endpoints that return immediate success on receive. Stands in for ManyChat."""
    def webhook(path: str, node_id: str, y: int, label: str) -> dict:
        return {
            "parameters": {
                "httpMethod": "POST",
                "path": path,
                "responseMode": "onReceived",
                "responseData": json.dumps({"status": "success", "endpoint": label}),
                "options": {},
            },
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2.1,
            "position": [200, y],
            "id": node_id,
            "name": f"Webhook {label}",
            "webhookId": path,
        }

    return {
        "name": MOCK_MC_NAME,
        "nodes": [
            webhook(MOCK_SET_FIELDS_PATH, "mock-set-fields", 100, "setCustomFields"),
            webhook(MOCK_ADD_TAG_PATH, "mock-add-tag", 300, "addTagByName"),
            webhook(MOCK_SEND_FLOW_PATH, "mock-send-flow", 500, "sendFlow"),
        ],
        "connections": {},
        "settings": {"executionOrder": "v1"},
    }


def build_ofm_workflow() -> dict:
    """Full-shape OFM workflow. Same as Joe's, minus the formatter LLM hop.

    Bella's system prompt now instructs her to use blank-line delimiters
    between IG bubbles. A deterministic Code node splits on `\\n\\n` and
    emits the same fields-array shape Joe produced. One less LLM call per
    turn, faster, cheaper, more reliable (no JSON-mode + tool-calling
    interaction risk).
    """
    system_msg = baked_system_message()

    mock_set_fields_url = f"{N8N_BASE_URL}/webhook/{MOCK_SET_FIELDS_PATH}"
    mock_add_tag_url = f"{N8N_BASE_URL}/webhook/{MOCK_ADD_TAG_PATH}"

    def tool_setfields(name: str, node_id: str, description: str, fields_json: str, y: int) -> dict:
        return {
            "parameters": {
                "toolDescription": description,
                "method": "POST",
                "url": mock_set_fields_url,
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
        }

    nodes = [
        # 1. WEBHOOK (input from chat.html)
        {
            "parameters": {
                "httpMethod": "POST",
                "path": OFM_WEBHOOK_PATH,
                "responseMode": "responseNode",
                "options": {},
            },
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2.1,
            "position": [200, 300],
            "id": "ofm-webhook",
            "name": "Webhook",
            "webhookId": OFM_WEBHOOK_PATH,
        },
        # 2. AI AGENT (Bella's brain)
        {
            "parameters": {
                "promptType": "define",
                "text": "={{ $json.body.message }}\n\nPrevious conversation summary: {{ $json.body.conversation_summary || 'New conversation' }}",
                "needsFallback": True,
                "options": {
                    "systemMessage": "=Subscriber ID: {{ $json.body.session_id }}\n\n" + system_msg,
                    "maxIterations": 10,
                },
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
        # 3. PRIMARY MODEL
        {
            "parameters": {
                "model": {"__rl": True, "value": "gpt-4o", "mode": "list", "cachedResultName": "gpt-4o"},
                "options": {"maxTokens": 2000, "temperature": 0.9},
            },
            "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
            "typeVersion": 1.2,
            "position": [400, 500],
            "id": "ofm-model",
            "name": "AI Model",
            "credentials": {"openAiApi": {"id": OPENAI_CRED_ID, "name": OPENAI_CRED_NAME}},
        },
        # 4. FALLBACK MODEL
        {
            "parameters": {
                "model": {"__rl": True, "value": "gpt-4o-mini", "mode": "list", "cachedResultName": "gpt-4o-mini"},
                "options": {"maxTokens": 2000, "temperature": 0.9},
            },
            "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
            "typeVersion": 1.2,
            "position": [500, 500],
            "id": "ofm-model-fallback",
            "name": "AI Model Fallback",
            "credentials": {"openAiApi": {"id": OPENAI_CRED_ID, "name": OPENAI_CRED_NAME}},
        },
        # 5. MEMORY
        {
            "parameters": {
                "sessionIdType": "customKey",
                "sessionKey": "={{ $json.body.session_id }}",
                "contextWindowLength": 30,
            },
            "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
            "typeVersion": 1.3,
            "position": [600, 500],
            "id": "ofm-memory",
            "name": "Memory",
        },
        # 6-10. THE FIVE TOOLS
        tool_setfields(
            "save_qualification_data",
            "tool-qual",
            "Fire ONCE at end of Phase 0 when both 18+ confirmed AND country known. Pass country, age, qualified.",
            '={\n  "subscriber_id": "{{ $(\'Webhook\').item.json.body.session_id }}",\n  "fields": [\n    {"field_name": "country", "field_value": "{{ $fromAI(\'country\', \'Country text\', \'string\') }}"},\n    {"field_name": "age", "field_value": "{{ $fromAI(\'age\', \'Age integer 18+\', \'number\') }}"},\n    {"field_name": "qualified", "field_value": "{{ $fromAI(\'qualified\', \'true or false\', \'string\') }}"}\n  ]\n}',
            700,
        ),
        tool_setfields(
            "save_discovery_data",
            "tool-disc",
            "Fire ONCE at end of Phase 2 before Phase 3 tease. Pass vibe, interests, why_followed, urgency_to_sub, mention_of_other_creators.",
            '={\n  "subscriber_id": "{{ $(\'Webhook\').item.json.body.session_id }}",\n  "fields": [\n    {"field_name": "vibe", "field_value": "{{ $fromAI(\'vibe\', \'Fans energy\', \'string\') }}"},\n    {"field_name": "interests", "field_value": "{{ $fromAI(\'interests\', \'Content style\', \'string\') }}"},\n    {"field_name": "why_followed", "field_value": "{{ $fromAI(\'whyFollowed\', \'How they found her\', \'string\') }}"},\n    {"field_name": "urgency_to_sub", "field_value": "{{ $fromAI(\'urgencyToSub\', \'High Medium Low\', \'string\') }}"},\n    {"field_name": "mention_of_other_creators", "field_value": "{{ $fromAI(\'mentionOfOtherCreators\', \'Mentioned other creators\', \'string\') }}"}\n  ]\n}',
            800,
        ),
        tool_setfields(
            "save_subscription_data",
            "tool-sub",
            "Fire ONCE in Phase 5 only after fan explicitly confirms they subscribed. Pass subbed, sub_tier, subbed_timestamp.",
            '={\n  "subscriber_id": "{{ $(\'Webhook\').item.json.body.session_id }}",\n  "fields": [\n    {"field_name": "subbed", "field_value": "{{ $fromAI(\'subbed\', \'true or false\', \'string\') }}"},\n    {"field_name": "sub_tier", "field_value": "{{ $fromAI(\'subTier\', \'Tier text\', \'string\') }}"},\n    {"field_name": "subbed_timestamp", "field_value": "{{ $fromAI(\'subbedTimestamp\', \'ISO datetime\', \'string\') }}"}\n  ]\n}',
            900,
        ),
        tool_setfields(
            "update_conversation_state",
            "tool-state",
            "Fire on every phase transition and mid-phase in 2-4. Pass current_phase (0-5) and conversation_summary (under 200 words).",
            '={\n  "subscriber_id": "{{ $(\'Webhook\').item.json.body.session_id }}",\n  "fields": [\n    {"field_name": "current_phase", "field_value": "{{ $fromAI(\'currentPhase\', \'0-5\', \'number\') }}"},\n    {"field_name": "conversation_summary", "field_value": "{{ $fromAI(\'conversationSummary\', \'Under 200 words\', \'string\') }}"}\n  ]\n}',
            1000,
        ),
        {
            "parameters": {
                "toolDescription": "Fire when a milestone is hit. Use exactly one of: Trust_Asset_Sent, OF_Link_Pitched, Subscribed, AI_Detection_Triggered, Disqualified_Lead, Human_Alert_Check_Prospect.",
                "method": "POST",
                "url": mock_add_tag_url,
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": '={\n  "subscriber_id": "{{ $(\'Webhook\').item.json.body.session_id }}",\n  "tag_name": "{{ $fromAI(\'tagName\', \'One of the 6 approved tags\', \'string\') }}"\n}',
                "options": {},
            },
            "type": "n8n-nodes-base.httpRequestTool",
            "typeVersion": 4.3,
            "position": [600, 1100],
            "id": "tool-tag",
            "name": "apply_tag",
        },
        # 11. CODE (split agent output on blank-line delimiter).
        # Bella's system prompt instructs her to put a blank line between
        # IG-style message bubbles. We split on \n\s*\n, cap at 6 bubbles
        # (the ManyChat AI > Answer 1..6 slot capacity), trim whitespace,
        # and emit the same fields-array shape Joe's workflow used so the
        # downstream Set AI Answers node stays identical to production.
        # This replaces the Message-a-model LLM hop with deterministic
        # string ops: one less LLM call, faster, cheaper, more reliable.
        {
            "parameters": {
                "jsCode": (
                    "let raw = $('AI Agent').first().json.output || '';\n"
                    "let text = typeof raw === 'string' ? raw : (raw.output || JSON.stringify(raw));\n"
                    "// Strip n8n langchain agent tool-trace leakage. The ToolsAgent V3\n"
                    "// sometimes prefixes/inlines '[Used tools: Tool: foo, Input: ..., Result: ...]'\n"
                    "// into its final text output. Those traces must never reach the fan.\n"
                    "text = text.replace(/\\[Used tools?: [^\\]]*?\\]\\s*/gs, '');\n"
                    "// Strip any leading whitespace left behind\n"
                    "text = text.replace(/^\\s+/, '').replace(/\\s+$/, '');\n"
                    "// Split on blank lines (one or more newlines with only whitespace between)\n"
                    "let parts = text.split(/\\n\\s*\\n+/).map(s => s.trim()).filter(Boolean);\n"
                    "// If the agent forgot to use blank-line splits, fall back to a single bubble\n"
                    "if (!parts.length) parts = [text.trim()];\n"
                    "// Cap at 6 bubbles to match ManyChat's AI > Answer 1..6 fields\n"
                    "if (parts.length > 6) {\n"
                    "  const tail = parts.slice(5).join('\\n\\n');\n"
                    "  parts = parts.slice(0, 5).concat([tail]);\n"
                    "}\n"
                    "const fields = parts.map((value, i) => ({ field_name: 'AI > Answer ' + (i + 1), field_value: value }));\n"
                    "return [{ json: {\n"
                    "  subscriber_id: $('Webhook').first().json.body.session_id,\n"
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
        # 12. SET AI ANSWERS (writes to mock ManyChat custom fields, parity with Joe)
        {
            "parameters": {
                "method": "POST",
                "url": mock_set_fields_url,
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify($json) }}",
                "options": {},
            },
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.3,
            "position": [1000, 300],
            "id": "ofm-set-answers",
            "name": "Set AI Answers",
        },
        # 13. RESPOND TO WEBHOOK (returns messages array to chat.html)
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
        "save_qualification_data": {"ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]},
        "save_discovery_data": {"ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]},
        "save_subscription_data": {"ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]},
        "update_conversation_state": {"ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]},
        "apply_tag": {"ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]},
    }

    return {
        "name": OFM_NAME,
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"},
    }


def main():
    # 1. Deploy Mock ManyChat first (OFM workflow tool nodes call it)
    print("\n=== Step 1: Mock ManyChat ===")
    mock_id = find_workflow_id(MOCK_MC_NAME)
    if mock_id:
        print(f"[info] existing mock workflow {mock_id}; deactivate + delete")
        deactivate(mock_id)
        delete_wf(mock_id)
    mock_wf = build_mock_manychat()
    mock_id = create_wf(mock_wf)
    activate(mock_id)
    print(f"[ok] Mock ManyChat deployed: id={mock_id}")
    print(f"     /webhook/{MOCK_SET_FIELDS_PATH}")
    print(f"     /webhook/{MOCK_ADD_TAG_PATH}")
    print(f"     /webhook/{MOCK_SEND_FLOW_PATH}")
    time.sleep(1)

    # 2. Deploy the full OFM workflow
    print("\n=== Step 2: OFM Full Workflow ===")
    ofm_id = find_workflow_id(OFM_NAME)
    if ofm_id:
        print(f"[info] existing OFM workflow {ofm_id}; deactivate + delete")
        deactivate(ofm_id)
        delete_wf(ofm_id)
    ofm_wf = build_ofm_workflow()
    # save local copy
    (SIM_DIR / "full_simulator_workflow.json").write_text(json.dumps(ofm_wf, indent=2))
    print(f"[ok] OFM workflow JSON saved locally")
    ofm_id = create_wf(ofm_wf)
    activate(ofm_id)
    print(f"[ok] OFM workflow deployed: id={ofm_id}")

    # 3. Clean up the old stripped-down workflow if present
    old_name = "OFM IG DM Agent SIMULATOR (Mia)"
    old_id = find_workflow_id(old_name)
    if old_id:
        print(f"\n=== Step 3: cleanup old simulator ===")
        deactivate(old_id)
        delete_wf(old_id)
        print(f"[ok] old workflow {old_id} deleted")

    print(f"\n=== DEPLOYED ===")
    print(f"Open in n8n UI:")
    print(f"   {N8N_BASE_URL}/workflow/{ofm_id}")
    print(f"\nWebhook URL (point chat.html here):")
    print(f"   {N8N_BASE_URL}/webhook/{OFM_WEBHOOK_PATH}")
    print(f"\nMock ManyChat workflow (so you can see tool-call payloads):")
    print(f"   {N8N_BASE_URL}/workflow/{mock_id}")
    print(f"\nTest:")
    print(f'   curl -X POST {N8N_BASE_URL}/webhook/{OFM_WEBHOOK_PATH} \\')
    print(f'     -H "Content-Type: application/json" \\')
    print(f'     -d \'{{"session_id":"test-1","message":"heyyy"}}\'')


if __name__ == "__main__":
    main()
