# V2: Selling Directly On OnlyFans (On-Platform Chat Bot)

EZJ's ask (2026-06-06): "Sell directly in the chat rooms as well. Not only on Instagram, but directly impact the revenue. How can we connect the bot to OnlyFans?"

V1 is the IG → OF sub conversion. V2 is the on-platform monetization layer where the real money is: pay-per-view (PPV) content sales, sexting upsells, custom requests, and tip-driven chat. Filipino chatter teams charge OFMs $1.5k to $3k per creator per month for exactly this layer. Replacing or augmenting that team is the second monetization unlock.

## TL;DR recommendation

Build a **human-in-the-loop draft assistant**, not a full autonomous bot. The chatter still presses send. The bot does the drafting, the personality, and the upsell math behind the scenes.

This is the only path that is (a) not a flat TOS violation, (b) ships in weeks not quarters, and (c) defensible if OF audits. It also matches what the smartest chatter agencies are quietly already doing.

## The five real options

### Option 1: Official OnlyFans API
Does not exist. OF has no public API for messaging, content, or sales. They have never opened one. Marketing partners get analytics; chatters get nothing. This door is closed.

### Option 2: Browser automation (Puppeteer / Playwright / Selenium)
Log into the creator's OF account in headless Chrome with her real credentials, drive the UI like a human. Bot polls inbox, sends messages, sets prices, sends PPV unlocks.

**Pros:** Total control. Can do anything a human can. No third-party dependency.

**Cons (severe):**
- OF fingerprints sessions (TLS, mouse movements, timing). Detection is aggressive.
- Confirmed accounts get **banned and creator loses all earnings + payout balance**.
- Requires per-creator residential proxy to look local.
- Breaks every time OF updates the front-end (every 2 to 4 weeks).
- One creator banned = chargebacks, lawsuits, dead pilot, dead product.

**Verdict:** High reward, very high downside. Some shady agencies do this. Not how we should anchor a productized service we plan to sell.

### Option 3: Reverse-engineered private API + cookies
Take an authenticated session cookie from the creator's logged-in OF browser session. Make API calls directly to OF's private endpoints (the ones their front-end uses internally). Open source toolchains exist (OnlySnarf, OFAPI wrappers on GitHub).

**Pros:** Cleaner than browser automation. No headless Chrome overhead.

**Cons:** Same TOS violation. Same ban risk. Endpoints change without notice. OF actively rate-limits and detects non-browser request patterns. Cookies expire and need re-auth.

**Verdict:** Marginally better than Option 2. Same fundamental risk profile.

### Option 4: Chatter dashboard platforms (Infloww, Supercreator, OFNotepad, Hubly)
These are CRM-style overlays that pro chatter agencies already use. They sit on top of OF and provide multi-conversation queues, message templates, PPV libraries, fan tagging, sale tracking. Most of them use a combination of Option 2 and Option 3 under the hood. The creator gives the platform her OF login; the platform provides the chat interface.

**Pros:** The agencies we're selling to **already pay for one of these**. Integration into their existing tool is a smaller ask than "install our bot."

**Cons:** None of them have public APIs. Integration means reverse-engineering their integration layer, which is reverse-engineering OF's underneath that. Or partnering with one of these tools as a vendor, which is a slow B2B sales motion.

**Verdict:** Long-term partnership play. Not V2.

### Option 5: Human-in-the-loop draft assistant (the play)
The chatter logs into OF in her real browser, exactly like normal. We ship one of:

- **A Chrome extension** that injects a side panel onto OF's chat UI. The panel reads the active conversation, calls our API, returns a suggested reply. Chatter clicks "Insert" and "Send". One human click per send.
- **A web dashboard** the chatter runs alongside her OF tabs. She pastes the latest fan message, gets a draft, copies it back. Higher friction than the extension but zero browser-automation dependency.
- **A Telegram/Slack bot** that gets a copy of each incoming OF message (via the chatter manually forwarding, or a screen-capture trigger), drafts a reply, the chatter approves and pastes back.

The bot drafts. The human sends. There is no automation, technically, because every send is a human keystroke.

**Pros:**
- No TOS violation. Real chatters use this style of assistant all the time (some quietly use ChatGPT). We're just productizing what they already do.
- Throughput multiplier: one chatter currently runs ~5 simultaneous conversations. With a draft assistant they run 15 to 25. **3-5x revenue per chatter labor hour.**
- Same Bella prompt framework, retargeted for on-platform conversion: PPV unlocks, sexting tier upsells, tip prompts, custom-content negotiation.
- Plug into the existing OFM workflow. No new tool the agency has to maintain.
- Ships in 2-3 weeks if we anchor on the Chrome extension.

**Cons:**
- Still requires a human chatter, so we're not replacing their team, we're 3-5x'ing it.
- Chatter could fall asleep on the job; throughput cap is still human.
- Chrome extension requires Chrome Web Store approval (1 to 2 weeks) or sideload only.

**Verdict:** This is the V2 to build. It's defensible, fast, and the value prop to OFMs is enormous (a chatter who was generating $8k/month for the agency now generates $25k to $40k/month with the same labor cost).

## Recommended V2 build (Chrome extension)

### Architecture

```
OnlyFans browser tab                                    n8n.ezjonline.com
  └─ Chrome extension content script                       /webhook/ofm-onplatform-<creator-handle>
      ├─ Reads active chat thread                          AI Agent (Sonnet 4.6 / GPT-4o)
      ├─ POSTs fan history + new message                   ├─ System prompt: Maya
      └─ Renders draft in side panel                       │   (on-platform Bella, retargeted)
          └─ Chatter clicks "Insert" → fills compose box   ├─ Knowledge base: creator's PPV
                                                           │   catalog, pricing tiers, scripts
                                                           └─ Returns draft + suggested price tag
```

### V2 system prompt persona: "Maya"

Bella's on-platform sister. Same warmth, but now the conversation has gone past the front door (the sub is paid). New objectives:

- PPV upsell: when a fan asks for "more" or "spicier", suggest a $10 to $30 PPV.
- Custom content close: when a fan asks for something specific, drive to her custom-request flow.
- Tip prompts: organic, low-frequency, after a positive interaction.
- Sexting tier upsell: she has paid sexting at $50 per session, surface it when emotional intensity is high.
- VIP/lock-in: 6-month renewals at a discount for fans showing retention signals.

Same hard limits as Bella (no minors, no contact off-platform, no chargebacks-prone payment methods).

### Knowledge base extension

Per-creator KB now includes a **PPV catalog** with descriptions, prices, and visibility states. The bot suggests which PPV to send based on the conversation thread.

### Build sprint (after V1 Harvey pilot proves)

| Day | Task |
|-----|------|
| 1 to 3 | Maya system prompt v1 |
| 4 to 7 | Chrome extension scaffold (Manifest V3), OF DOM selectors, side panel UI |
| 8 to 10 | n8n on-platform webhook + Maya agent |
| 11 to 14 | Per-creator PPV catalog KB structure, Harvey pilot creator catalog populated |
| 15 to 17 | End-to-end test with Harvey's chatter, iterate |
| 18 to 21 | Pilot with Harvey's chatter team for 1 creator, measure throughput uplift |
| 22 to 28 | Iterate, then roll to second Harvey creator |

### What we don't build in V2

- No autonomous send. Every send is human-clicked.
- No headless browser. The extension runs in the chatter's normal browser session.
- No OF account credentials stored on our side. We see only the conversation text the chatter is already looking at.
- No payment processing. PPV unlocks go through OF's native flow.

## Pricing impact

V2 changes the offer significantly. Setup fee per creator goes up (~$3k to cover extension config + PPV catalog build). Performance share gets richer because the value created is on-platform revenue (way bigger than IG sub revenue), not just sub count. **Re-run `/hormozi pricing` for V2 separately.**

## What stays gated

- Lawyer review on the V2 architecture before client deployment. Specifically: is reading the conversation thread via Chrome extension safe under OF TOS? It's a gray zone. Likely yes if the chatter is the OF account holder reading her own threads, but worth a 30-minute call with a tech lawyer ($500 spent now avoids a $50k issue later).
- Harvey buy-in on V2. He may want to keep his existing chatter team intact even after V2 (they still handle on-platform sends). The pitch reframes from "replace the team" to "the team makes 3-5x more revenue with the same hours".

## Bottom line for EZJ

V1 sells the IG conversion. Ship Harvey pilot, measure attributable subs.

V2 is the bigger MRR unlock. The Chrome extension assistant is the only path that ships in weeks not quarters and doesn't put creator accounts at risk. Building it has a clear sequence: prove V1, capture the case study, pitch V2 to Harvey as an expansion, build the extension over 3 weeks, second pilot.

Do NOT build Options 1 to 4. They get accounts banned, kill the pilot, kill the product.

When V1 is at ≥10 attributable subs and Harvey has signed a V2 expansion, open `phases/05_v2_chrome_extension.md` and run.
