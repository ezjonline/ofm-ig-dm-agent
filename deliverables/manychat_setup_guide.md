# ManyChat Setup Guide — Per-Creator Deployment

Follow this checklist for every new creator. Estimated time: 60-90 minutes once the n8n workflow template is in place.

## Prerequisites

- Creator's IG account has a Business or Creator profile (required for ManyChat).
- Creator's IG account is connected to a Facebook Page (Meta requirement for IG inbox API access).
- ManyChat Pro plan ($15/mo per page minimum, OFM pays).
- EZJ added as collaborator on the creator's ManyChat workspace.
- n8n workflow template at `n8n_workflow_ofm_v1.json` already imported and EZJ has admin access on `n8n.ezjonline.com`.

## Step 1: Create the ManyChat app

1. In ManyChat, click + > "Add Account" > Instagram.
2. Connect to the creator's IG account (auth flow).
3. Connect the underlying Facebook Page if not already linked.
4. Confirm IG DM permissions are granted (Inbox, Send Message, Read Message).

## Step 2: Create the custom fields

In ManyChat > Settings > Custom Fields, create these. Type must match exactly.

| Field name | Type | Purpose |
|------------|------|---------|
| `country` | Text | Set by save_qualification_data |
| `age` | Number | Set by save_qualification_data |
| `qualified` | Text | Set by save_qualification_data (stored as "true"/"false") |
| `current_phase` | Number | Set by update_conversation_state |
| `conversation_summary` | Long Text | Set by update_conversation_state |
| `vibe` | Text | Set by save_discovery_data |
| `interests` | Text | Set by save_discovery_data |
| `why_followed` | Text | Set by save_discovery_data |
| `urgency_to_sub` | Text | Set by save_discovery_data |
| `mention_of_other_creators` | Text | Set by save_discovery_data |
| `subbed` | Text | Set by save_subscription_data (stored as "true"/"false") |
| `sub_tier` | Text | Set by save_subscription_data |
| `subbed_timestamp` | Text | Set by save_subscription_data (ISO datetime) |
| `AI > User Messages` | Text | Holds the incoming user message for the webhook |
| `AI > Answer 1` | Text | First split message |
| `AI > Answer 2` | Text | Second split message |
| `AI > Answer 3` | Text | Third split message |
| `AI > Answer 4` | Text | Fourth split message |
| `AI > Answer 5` | Text | Fifth split message |
| `AI > Answer 6` | Text | Sixth split message |

## Step 3: Build the trigger flows

### Flow 3.1: Story-react auto-DM
- Trigger: Instagram > Story Reaction > Any
- Action: Set custom field `AI > User Messages` to `{{Last User Free Input}}` (or the story-reaction emoji if no text).
- Action: External Request → POST to `https://n8n.ezjonline.com/webhook/ofm-ig-dm-<CREATOR_HANDLE>` with body `{{$ContactJson}}` (ManyChat's full subscriber JSON).
- Wait for webhook response.
- Action: Run "Send AI Answers Flow" (Flow 3.5).

### Flow 3.2: Comment-trigger auto-DM
- Trigger: Instagram > Comment on Post > Any keyword (or specific keyword like "info").
- Action: Same as Flow 3.1.

### Flow 3.3: Cold inbound DM
- Trigger: Instagram > Conversation Started.
- Action: Set `AI > User Messages` to the incoming message text.
- Action: External Request to n8n webhook (same as 3.1).
- Action: Run Flow 3.5.

### Flow 3.4: Recurring inbound (any subsequent DM from same fan)
- Trigger: Instagram > Default Reply.
- Same actions as Flow 3.3.

### Flow 3.5: Send AI Answers Flow
This is the flow that fires from inside n8n's `Send Flow` HTTP node. Configure:
- Flow type: Send Message > Instagram
- Block 1: Send `{{AI > Answer 1}}` if not empty.
- Block 2: Send `{{AI > Answer 2}}` if not empty.
- Block 3: Send `{{AI > Answer 3}}` if not empty.
- Block 4: Send `{{AI > Answer 4}}` if not empty.
- Block 5: Send `{{AI > Answer 5}}` if not empty.
- Block 6: Send `{{AI > Answer 6}}` if not empty.

Set typing delay 1.5-2.5 seconds between blocks for realism.

Note: Copy the Flow Namespace from Flow 3.5 (found under flow URL or via ManyChat API). Paste this into the n8n `Send Flow` node's `flow_ns` field.

## Step 4: Generate ManyChat bearer token

1. In ManyChat > Settings > API.
2. Generate a new API token (label it `n8n-<creator-handle>`).
3. Copy the token.
4. In n8n > Credentials > New > HTTP Bearer Auth, paste the token. Name it `<CREATOR_HANDLE> ManyChat Bearer`.
5. Copy the credential ID from n8n.
6. In the cloned n8n workflow, replace every `<MANYCHAT_BEARER_CRED_ID>` placeholder with this ID. (The 6 tool nodes + Send Flow + Set AI Answers all need it.)

## Step 5: Wire the webhook

1. In the cloned n8n workflow, the Webhook node path is `ofm-ig-dm-<CREATOR_HANDLE>`. Confirm the full URL is `https://n8n.ezjonline.com/webhook/ofm-ig-dm-<CREATOR_HANDLE>`.
2. In each ManyChat External Request action, paste this URL.
3. Activate the n8n workflow.

## Step 6: Wire the Send Flow

1. In the n8n workflow's `Send Flow` HTTP node, replace `<MANYCHAT_SEND_FLOW_NS>` with the Flow 3.5 namespace.

## Step 7: End-to-end smoke test

Send a test inbound DM to the creator's IG from a different account. Watch:
1. ManyChat triggers Flow 3.3.
2. ManyChat External Request fires the webhook.
3. n8n executes: Webhook → AI Agent (with tool calls) → Message a model → Code → Set AI Answers → Send Flow.
4. ManyChat receives the Send Flow call, fires Flow 3.5, sends messages.
5. The test IG account receives the messages.

If any step fails, check n8n execution log and ManyChat live chat log.

## Step 8: Go live

1. Toggle ManyChat triggers from "Draft" to "Active".
2. Confirm the IG account is set to Business/Creator (DMs API will not deliver to personal accounts).
3. EZJ monitors first 24 hours.

## Common issues

- **Webhook returns 200 but no messages send back.** ManyChat custom fields may not be populating. Check the n8n `Set AI Answers` node payload for proper field names (case-sensitive, including spaces: `AI > Answer 1`).
- **Bot replies in the wrong creator's voice.** Knowledge base doc URL is wrong in the n8n `Knowledge base` node. Verify per-creator.
- **Sessions mix up between fans.** Session key in n8n Memory node not unique enough. Confirm format `ofm_<CREATOR_HANDLE>_{{ ig_username }}`.
- **`AI > User Messages` field not populating.** ManyChat trigger flow's first action must explicitly set this field before the External Request fires.
- **Messages contain dashes.** System prompt is doing its job but formatter is letting them through. Check formatter prompt v1 has the no-dashes rule active.
