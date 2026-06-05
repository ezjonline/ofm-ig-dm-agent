# Phase 2: Harvey pilot deployment

Status: ⬜ Not started
Owner: EZJ + Harvey (Monetize.me)
Output: Live IG DM bot running on one of Harvey's creators

## Step 2.1: Confirm Tom's status on the $700 onboarding-form deal ❓ Blocked

We owe Harvey a status check before pitching the bot upsell. Per memory `project_harvey_monetize_me_2026-06-02.md`, the original $700 onboarding-form project was a soft yes pending Tom (Harvey's business partner) approval. Three branches:

- **Tom green-lights the form:** ship the form fast, then pitch the IG bot as a follow-on separate scope.
- **Tom is still cold:** reframe the pitch. Skip the $700 form, pitch the bot direct at the right price. This likely closes harder because it's the higher-leverage offer.
- **Tom kills both:** drop Harvey as the anchor, go straight to outbound (Phase 4) and find another OFM willing to pilot.

Action: EZJ messages Harvey for status. One Telegram message, no follow-ups until reply.

## Step 2.2: Harvey nominates a pilot creator ✅ Locked · ⬜ Not started

Once Harvey is greenlit, ask him for one creator who fits these criteria:
- Lower stakes (NOT his top earner; we want to iterate without high-revenue risk)
- 5k-50k IG follower count
- Active IG (3+ posts/week, active stories)
- Communicative creator (responds to Harvey's messages, can give us voice samples)
- Existing OF page with a defined sub price ($9-$30/mo range ideal)

Harvey returns: creator name, IG handle, OF URL, monthly OF revenue baseline.

## Step 2.3: Build the per-creator knowledge base doc ✅ Locked · ⬜ Not started

A Google Doc per creator. The LLM agent's `Knowledge base` tool calls this doc whenever the prospect asks something creator-specific.

Template at `../deliverables/creator_knowledge_base_template.md` (to build during this phase). Sections:

- **Creator basics:** name, IG handle, OF handle, age, location (kept vague for safety), niche/aesthetic.
- **Voice samples:** 5-10 real DMs she has written (pulled with Harvey's permission). The bot mimics this.
- **Content pillars behind the paywall:** categories only, no explicit detail (e.g. "lifestyle, photoshoots, exclusive video drops, custom requests").
- **Pricing tiers:** OF monthly sub price, current promo, custom content starting price (e.g. "videos from $20, photos from $10").
- **Hard NOs:** off-limit topics, kinks she won't engage with, names she won't go by.
- **Suggested teasers:** 2-3 IG-safe (non-explicit) preview asset descriptions she's pre-approved for the bot to reference.

EZJ creates the doc, shares edit access with EZJ + Harvey + the creator. Drop the doc URL into the n8n `Knowledge base` node.

## Step 2.4: Provision ManyChat for the creator's IG ✅ Locked · ⬜ Not started

Per the ManyChat setup guide (to build at `../deliverables/manychat_setup_guide.md`).

Per-creator steps:
1. Harvey invites EZJ as a collaborator on the creator's IG ManyChat account (or creates one if she doesn't have one).
2. EZJ creates the custom fields (matches Joe's pattern but renamed):
   - `country` (text), `age` (number), `current_phase` (number 0-6), `conversation_summary` (long text)
   - `vibe`, `interests`, `urgency_level`, `subbed` (bool)
   - `AI > User Messages`, `AI > Answer 1` through `AI > Answer 6`
3. EZJ creates the trigger flows:
   - Story-react auto-DM trigger
   - Comment-trigger auto-DM on creator's posts
   - Cold inbound DM trigger (any keyword)
   - Opener flow (sends an initial message + sets `current_phase = 0`)
4. EZJ creates the External Request action that posts the ManyChat subscriber payload to the n8n webhook URL.
5. EZJ creates the Send Flow that pushes the formatted `AI > Answer N` messages back into the DM thread.
6. Generate a fresh ManyChat bearer auth token and paste into the n8n workflow's credentials.

## Step 2.5: End-to-end test before going live ✅ Locked · ⬜ Not started

Before flipping live on the creator's real IG:
1. Test with EZJ's @ezjcreative IG account (or a burner). Send the trigger keyword, walk through Phase 0 to Phase 5.
2. Verify every `update_conversation_state` call fires on phase transition.
3. Verify `save_subscription_data` fires only after explicit sub confirmation.
4. Verify no dashes in any output (grep the AI response stream).
5. Verify the 5 adversarial inputs hit the safety guardrails (see Phase 1 verification list).

## Step 2.6: Go live + monitor for 7 days ✅ Locked · ⬜ Not started

Flip the ManyChat triggers on for the creator's real IG account. Monitor in real time for 7 days:
- Day 1-2: every conversation reviewed within 30 minutes. EZJ iterates the system prompt if anything is off.
- Day 3-7: spot-checked daily. EZJ updates the knowledge base doc as creator-specific edge cases surface.
- Day 7: 30-day metric tracking begins.

## Verification before Phase 3 begins

- [ ] Pilot creator picked
- [ ] Knowledge base doc populated and accessible
- [ ] ManyChat fully configured with all custom fields + triggers + send flows
- [ ] End-to-end test passed
- [ ] Bot live for 7 days with EZJ monitoring
- [ ] At least 3 conversations reached Phase 5 (OF link pitch) without manual intervention
