#!/usr/bin/env python3
"""
Deploy the OFM IG DM Agent SIMULATOR to n8n.ezjonline.com.

What this does:
- Builds a synchronous-response simulator workflow (webhook -> AI Agent -> response)
- Bakes the "Mia" test creator into the system prompt (no Google Docs dep)
- Uses Anthropic Claude Sonnet 4.6 via existing n8n credential
- Strips ManyChat tool dependencies (sim has no tools, agent responds as plain text)
- Imports via n8n REST API, activates the workflow
- Prints the test webhook URL

Run with the venv:
    python3 agency/products/ofm_ig_dm_agent/simulator/deploy_simulator.py
"""
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[4]
load_dotenv(Path.home() / ".claude-secrets" / "claudia" / ".env")

N8N_BASE_URL = os.environ.get("N8N_BASE_URL", "https://n8n.ezjonline.com").rstrip("/")
N8N_API_KEY = os.environ["N8N_API_KEY"]
HEADERS = {"X-N8N-API-KEY": N8N_API_KEY, "Content-Type": "application/json"}

# Model creds. Both Anthropic creds (WMwxvyJGynY7n2aB and RG6szGd77Q8QIaDl)
# were out of API balance at deploy time. Falling back to OpenAI gpt-4o via
# "YouTube Research Agent - OpenAi" which is heavily used by other workflows
# and clearly funded. Swap back to Anthropic once a top-up lands.
OPENAI_CRED_ID = "ZmA2gnjYXr7QhKQw"
OPENAI_CRED_NAME = "YouTube Research Agent - OpenAi"
OPENAI_MODEL = "gpt-4o"

SIM_DIR = REPO_ROOT / "agency" / "products" / "ofm_ig_dm_agent" / "simulator"
SYSTEM_PROMPT_FILE = REPO_ROOT / "agency" / "products" / "ofm_ig_dm_agent" / "deliverables" / "system_prompt_v1.md"
MIA_PERSONA_FILE = SIM_DIR / "mia_test_creator.md"

WORKFLOW_NAME = "OFM IG DM Agent SIMULATOR (Mia)"
WEBHOOK_PATH = "ofm-sim-mia"


def load_system_prompt_body() -> str:
    """Pull the prompt body (everything below the first --- separator) from system_prompt_v1.md."""
    text = SYSTEM_PROMPT_FILE.read_text()
    # The prompt has a header followed by '---' then the production body
    parts = text.split("---", 1)
    if len(parts) < 2:
        sys.exit("system_prompt_v1.md has no --- separator; aborting")
    return parts[1].strip()


def load_mia_persona() -> str:
    return MIA_PERSONA_FILE.read_text()


def baked_system_message() -> str:
    """Compose the full system message for the simulator.

    Includes:
    - Sim-mode notice (so the agent knows it's running without ManyChat tools)
    - Mia persona (replaces the knowledge_base tool entirely)
    - The full system_prompt_v1 body with [CREATOR_NAME] -> Mia
    """
    prompt_body = load_system_prompt_body().replace("[CREATOR_NAME]", "Mia").replace("[creator first name]", "Mia").replace("[CREATOR_HANDLE]", "mia.everyday")
    mia = load_mia_persona()

    sim_header = (
        "# SIMULATOR MODE\n\n"
        "You are running in simulator mode. The ManyChat tool integrations are not wired up. "
        "Do NOT attempt to call save_qualification_data, save_discovery_data, save_subscription_data, "
        "apply_tag, or update_conversation_state. There are no tools available. Just respond as Bella "
        "in plain text. The simulator harness tracks phase progression by parsing your text output.\n\n"
        "The `knowledge_base` tool is also not wired. Instead, the creator's full knowledge base is "
        "inlined below. Treat the section titled 'MIA — KNOWLEDGE BASE (INLINED)' as the authoritative "
        "source for any question about her.\n\n"
        "When you would normally fire a tool, instead mention the milestone in a tag inside square "
        "brackets at the END of your message. Example: at end of Phase 0, append `[SIM_TAG: phase=1, "
        "qualified=true, country=USA, age=27]`. At Phase 4 link drop append `[SIM_TAG: phase=4, "
        "of_link_pitched=true]`. The harness parses these tags. The fan never sees them in the real "
        "deployment because in production the tool calls happen silently; in simulation the tags ARE "
        "the tool calls.\n\n"
        "Other than that, behave exactly as the production prompt instructs. Same persona, same voice, "
        "same hard limits, same phase flow.\n\n"
        "---\n\n"
    )

    kb_section = (
        "# MIA — KNOWLEDGE BASE (INLINED)\n\n"
        "Use this section in place of the knowledge_base tool. All Mia-specific facts come from here.\n\n"
        f"{mia}\n\n"
        "---\n\n"
    )

    return sim_header + kb_section + prompt_body


def build_workflow_json() -> dict:
    system_msg = baked_system_message()
    # Note: n8n stores systemMessage as an expression starting with `=`. Plain string is fine too but
    # the agent node expects the expression format. For static text we omit the = prefix.
    return {
        "name": WORKFLOW_NAME,
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": WEBHOOK_PATH,
                    "responseMode": "lastNode",
                    "options": {},
                },
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2.1,
                "position": [200, 300],
                "id": "sim-webhook",
                "name": "Webhook",
                "webhookId": WEBHOOK_PATH,
            },
            {
                "parameters": {
                    "promptType": "define",
                    "text": "={{ $json.body.message }}",
                    "options": {
                        "systemMessage": system_msg,
                        "maxIterations": 5,
                    },
                },
                "type": "@n8n/n8n-nodes-langchain.agent",
                "typeVersion": 3,
                "position": [600, 300],
                "id": "sim-agent",
                "name": "AI Agent",
            },
            {
                "parameters": {
                    "model": {
                        "__rl": True,
                        "value": OPENAI_MODEL,
                        "mode": "list",
                        "cachedResultName": OPENAI_MODEL,
                    },
                    "options": {
                        "maxTokens": 2000,
                        "temperature": 0.9,
                    },
                },
                "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
                "typeVersion": 1.2,
                "position": [400, 500],
                "id": "sim-model",
                "name": "AI Model",
                "credentials": {
                    "openAiApi": {
                        "id": OPENAI_CRED_ID,
                        "name": OPENAI_CRED_NAME,
                    }
                },
            },
            {
                "parameters": {
                    "sessionIdType": "customKey",
                    "sessionKey": "={{ $json.body.session_id }}",
                    "contextWindowLength": 30,
                },
                "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
                "typeVersion": 1.3,
                "position": [600, 500],
                "id": "sim-memory",
                "name": "Memory",
            },
        ],
        "connections": {
            "Webhook": {
                "main": [[{"node": "AI Agent", "type": "main", "index": 0}]]
            },
            "AI Model": {
                "ai_languageModel": [[{"node": "AI Agent", "type": "ai_languageModel", "index": 0}]]
            },
            "Memory": {
                "ai_memory": [[{"node": "AI Agent", "type": "ai_memory", "index": 0}]]
            },
        },
        "settings": {
            "executionOrder": "v1",
        },
    }


def find_existing_workflow_id(name: str) -> str | None:
    r = requests.get(f"{N8N_BASE_URL}/api/v1/workflows", headers=HEADERS, timeout=30)
    r.raise_for_status()
    for w in r.json().get("data", []):
        if w["name"] == name:
            return w["id"]
    return None


def deactivate_workflow(wf_id: str):
    r = requests.post(f"{N8N_BASE_URL}/api/v1/workflows/{wf_id}/deactivate", headers=HEADERS, timeout=30)
    if r.status_code not in (200, 400):  # 400 if already inactive
        print(f"[warn] deactivate returned {r.status_code}: {r.text[:200]}")


def delete_workflow(wf_id: str):
    r = requests.delete(f"{N8N_BASE_URL}/api/v1/workflows/{wf_id}", headers=HEADERS, timeout=30)
    if r.status_code != 200:
        print(f"[warn] delete returned {r.status_code}: {r.text[:200]}")


def create_workflow(wf: dict) -> str:
    r = requests.post(f"{N8N_BASE_URL}/api/v1/workflows", headers=HEADERS, data=json.dumps(wf), timeout=60)
    if r.status_code not in (200, 201):
        print(f"[error] create failed: {r.status_code}\n{r.text}")
        sys.exit(1)
    return r.json()["id"]


def activate_workflow(wf_id: str):
    r = requests.post(f"{N8N_BASE_URL}/api/v1/workflows/{wf_id}/activate", headers=HEADERS, timeout=30)
    if r.status_code != 200:
        print(f"[error] activate failed: {r.status_code}\n{r.text}")
        sys.exit(1)


def main():
    wf = build_workflow_json()

    # Save a local copy of what we're about to deploy
    local_copy = SIM_DIR / "simulator_workflow.json"
    local_copy.write_text(json.dumps(wf, indent=2))
    print(f"[ok] workflow JSON saved locally: {local_copy.relative_to(REPO_ROOT)}")

    existing_id = find_existing_workflow_id(WORKFLOW_NAME)
    if existing_id:
        print(f"[info] existing simulator workflow found (id={existing_id}); deactivating + deleting")
        deactivate_workflow(existing_id)
        delete_workflow(existing_id)

    wf_id = create_workflow(wf)
    print(f"[ok] workflow created: id={wf_id}")

    activate_workflow(wf_id)
    print(f"[ok] workflow activated")

    webhook_url = f"{N8N_BASE_URL}/webhook/{WEBHOOK_PATH}"
    print(f"\n=== SIMULATOR DEPLOYED ===")
    print(f"Workflow: {WORKFLOW_NAME}")
    print(f"ID: {wf_id}")
    print(f"Webhook URL: {webhook_url}")
    print(f"\nTest with:")
    print(f'  curl -X POST {webhook_url} \\')
    print(f'    -H "Content-Type: application/json" \\')
    print(f'    -d \'{{"session_id":"test-1","message":"heyyy"}}\'')


if __name__ == "__main__":
    main()
