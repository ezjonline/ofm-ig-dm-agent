<!-- Generated 2026-06-13 by the hoexa-ban-safety-doctrine research workflow. 6 ban surfaces, each adversarially verified, fact separated from vendor folklore. Living doc, re-verify soft numbers against live Meta/provider dashboards before launch. -->

# Hoexa Ban-Safety Doctrine

The enforceable rulebook the team builds and operates by. Weighted to the adversarial verdicts: heavy on `solid` surfaces (meta-ai-account-bans-2026, prospecting-outreach-safety, llm-and-payment-tos), demoted on the `partly_real` numeric folklore in the link-practices, DM-automation, and isolation surfaces.

## TL;DR (the 5 rules that, if broken, kill the business)

1. **Official Graph API only, never a password.** Run the IG DM agent exclusively through ManyChat on the Instagram Graph API. No browser bots, Chrome extensions, Selenium, or any tool that asks for an IG password. This is the single confirmed line between "Meta Business Partner that survived the ban wave" and "permanently banned." (Verified: ManyChat is an official Meta Business Partner; unofficial automation is the genuine high-risk vector, per the multi-account verdict.)

2. **No cold outbound, ever, from any creator account.** There is no compliant API path for an unsolicited first DM in 2026. Every conversation must start from a user action (comment keyword, Story reply, follow, inbound opener). Cold DMing is the confirmed single fastest path to a permanent ban (creatorflow, spurnow, prospecting verdict = `solid`).

3. **No AI agent gets ungated write access to any Meta API.** The confirmed "Claude Code terminated the whole business portfolio in ~1 week" case was caused by autonomous write access plus inhuman call cadence plus aggressive retries, not the Anthropic name. Reads can be automated; every write passes a human-approval gate. Use Meta's official Ads MCP (mcp.facebook.com/ads, Business OAuth, launched April 29 2026) for any ads automation (meta-ai-bans verdict = `solid`).

4. **Isolate the money rail and the LLM org from EZJ Online LLC.** Run Hoexa on a dedicated Anthropic organization and a separate legal entity / EIN / bank / Stripe descriptor. A single OF-use-case flag on a shared Anthropic org can suspend the whole org (keys keep billing, no SLA). A for-cause Stripe termination can land the business on the MATCH/TMF list for 5 years, blocking nearly every processor (llm-and-payment verdict = `solid`, verbatim-confirmed against Anthropic AUP and Stripe restricted-business list).

5. **One creator = one fully isolated stack, and never build an account farm.** One IG account, one Facebook Page, one router/hub, one custom-field namespace per creator. Our B2B outreach accounts and Apify scraping live on entirely separate infrastructure. The product runs ManyChat on the creator's own aged, real account, not on a fleet of fresh burners we spin up. Owning a farm is scope creep into the exact catastrophic mass-ban surface the safe path avoids.

## Threat Matrix

| Surface | Severity | Top ban trigger | Top mitigation | Verdict |
|---|---|---|---|---|
| meta-ai-account-bans-2026 | Critical | AI agent with ungated write access to Meta API + inhuman cadence + retries | Read-only default, human-gated writes, official Ads MCP (Business OAuth) | **solid** |
| llm-and-payment-tos | Critical | Model generates explicit content (Anthropic AUP) / Stripe reclassifies as adult, MATCH listing | Suggestive-only by design, dedicated Anthropic org, separate entity + high-risk processor standby | **solid** |
| prospecting-outreach-safety | High | Cold unsolicited DMs to OFM operators (no compliant path) | Shift to user-initiated triggers, genuinely low volume, warm-up gate | **solid** |
| ig-dm-automation-policy | Critical | Cold outbound / unofficial automation / password-based tools | Graph API only, user-initiated triggers only, 24h window enforced | **partly_real** (architecture solid, numbers vendor-sourced) |
| ig-creator-link-practices | Critical | Raw onlyfans.com URL in any public field; Linktree for an OF account | Clean adult-permissive hub (Beacons/AllMyLinks/custom domain), link delivered only in-window in DM | **partly_real** (policy scaffolding real, "DMs escape scanning" is an unproven vendor claim) |
| multi-account-isolation | Critical | Shared IP/device/phone across accounts; automating before warm-up | One-account-one-stack hygiene, warm-up before automation, scrape logged-out | **partly_real** (spine confirmed, several numbers invented) |

## Non-Negotiables

Hard rules to bake into the product and ops. Each is enforceable in code, config, or SOP.

1. **Graph API only.** Reject any architecture, tool, or vendor using browser automation, UI scripting, screen scraping, or an IG password. If it is not the official Messaging API via a Meta Business Partner (ManyChat-class), it does not ship. Require a Professional (Creator/Business) account linked to a Facebook Page as a setup precondition; personal accounts have no compliant path.

2. **No cold outbound from creator accounts, ever.** Every flow node originates from a user-initiated trigger (comment keyword, Story reply/mention, follow, inbound DM, ad click). Encode as a non-bypassable workflow precondition. Confirmed verbatim against Meta's Messaging API docs: the user must message first, then a 24-hour window opens.

3. **Enforce the 24-hour window in the engine.** Tag every contact with last-inbound timestamp. Block any automated promo send when now minus last_inbound exceeds 24h. The window resets on each new inbound user message. Apply `HUMAN_AGENT` (the 7-day extension) only on a genuine human action; Meta detects bot misuse and revokes API access. (Confirmed against Meta docs.)

4. **AI disclosure fires at conversation start and on human/bot handoff.** Use the approved assistant persona ("I'm her assistant who runs her DMs while she's shooting"). This is a Meta developer-policy requirement, an Anthropic AUP requirement (disclose "at the beginning of each chat session"), and legally mandatory for California users under the Bot Disclosure Law (CA B&P Code 17940). Bake into Phase 0 of the system prompt as a non-removable node.

5. **18+ age gate fails CLOSED at Phase 0.** If 18+ cannot be confirmed, hard-exit via the warm under-18 path (free public content link, no further engagement). No sexualized content reaches an unverified or under-18 user. Minor-safety is the one absolute: Anthropic defines a minor as anyone under 18 regardless of jurisdiction and reports CSAM/minor enticement to authorities (confirmed verbatim against the AUP).

6. **System prompt hard-bans explicit generation.** Non-overridable ban on sexual intercourse, sex acts, erotica, fetish/fantasy content, and erotic chat, mirroring Anthropic's exact AUP prohibited list ("Depict or request sexual intercourse or sex acts", "Generate content related to sexual fetishes or fantasies", "Engage in erotic chats", all verbatim-confirmed). Suggestive is the ceiling; explicit lives behind the OF paywall only.

7. **Pre-send content filter on every outbound DM, fail-closed.** Pattern-based (not static blocklist): block explicit terms (NSFW/XXX/PPV/hardcore), off-platform redirects (WhatsApp/Telegram/Snapchat/PayPal/Venmo/CashApp), raw phone/email/crypto strings, competitor platform names, leetspeak obfuscation of platform names, and all dashes. Run Anthropic's free moderation endpoint or a cheap classifier; block-and-rewrite before send. There is no official Meta wordlist, so the filter is pattern-based and continuously updated, never treated as complete.

8. **Never emit a raw onlyfans.com URL in any DM or public field.** The agent may only send the creator's configured hub/router URL. Store the OF link nowhere the agent can paste it directly. Per-creator config must specify an adult-permissive router (Beacons or AllMyLinks default, custom domain ideal). `linktr.ee` is a banned config value with a hard validation reject. (Linktree's 2026 TOS bars adult content; Beacons allows it with a content warning; AllMyLinks explicitly welcomes adult creators, all confirmed.)

9. **AI agents are read-only by default on every Meta API.** Any write path (publish creative, shift budget, edit campaign) passes through a human-approval queue, not direct agent-to-API writes. For ads automation, mandate Meta's official Ads MCP/CLI (mcp.facebook.com/ads, Business OAuth, never raw/personal tokens). Implement exponential backoff on error 613 and all 4xx/5xx; never retry in a tight loop.

10. **One creator = one isolated stack.** One IG account, one Facebook Page, one router/hub, one custom-field namespace, no shared hub domain across creators (a flagged domain poisons every account using it). Default to running on the creator's existing aged real account on her own device/SIM, not a fresh burner.

11. **Hoexa runs on a dedicated Anthropic org and a separate legal entity.** No shared API keys or billing with EZJ Online's primary Claude org. Separate EIN, bank account, and Stripe descriptor. Billing structured as B2B agency/SaaS services invoiced to OFM agencies (setup + performance share), never fan-facing adult payments. The billed entity, its website, and the card descriptor carry zero explicit content and zero OF branding.

12. **Stand up a high-risk processor before you need it, and never exit a processor for-cause.** Keep one adult-experienced acquirer (CCBill / Corepay / PayKings / PaymentCloud tier) warm as a hot standby alongside Stripe. Hold a multi-month cash reserve outside the primary processor to survive a rolling hold (documented case: $16,448 frozen 6+ months). If any processor signals discomfort, initiate a clean voluntary close, which typically does not list you; a for-cause termination can trigger the 5-year MATCH listing.

13. **Scraping is logged-out, throttled, and decoupled.** Apify runs logged-out public data only, on its own proxies, never tied to any creator or outreach login or IP. Bright Data v. Meta (N.D. Cal., Judge Chen, Jan 2024, Meta dropped appeal Feb 2024) protects logged-off public scraping from contract/CFAA liability. Note: that ruling addresses legality, not ban-risk; a logged-out scrape can still get an IP blocked, so stay throttled.

14. **Migrate off deprecated message tags.** `CONFIRMED_EVENT_UPDATE`, `ACCOUNT_UPDATE`, and `POST_PURCHASE_UPDATE` return error 100 (deprecation confirmed via Meta's Messenger Platform changelog; exact date reported as April 27 2026 but re-verify against the live changelog before launch). Use the standard 24h window plus Utility Templates / Marketing Messages API for re-engagement.

15. **Kill-switch and health monitor per account.** Reach/impression drop monitoring, send-error spikes, restriction notices. On a flag: stop the triggering behavior, pause, file one appeal, resume SFW. Log every send so the blast radius of any flag is auditable. Build for account loss as a normal event, not an edge case (Meta's Oversight Board flagged due-process and appeal-review gaps, June 4 2026, TechCrunch confirmed).

## Per-Surface Playbook

### 1. meta-ai-account-bans-2026 (verdict: solid)

**Triggers.** Autonomous AI agent with ungated write access to a Meta API, retrying on errors until anomaly detection flags inhuman cadence (the confirmed Claude Code portfolio-termination case). Sustained rate-limit violations (error 613, pushing past Business Use Case quota in the `X-Business-Use-Case-Usage` header). Raw personal tokens instead of scoped Business OAuth. Browser automation / scripted login (Meta fingerprints scripted timing and the TLS handshake before HTTP headers transmit). Connected-account contagion: one tripped asset can auto-suspend all linked assets.

**Mitigations and build rules.**
- Mandate Meta's official Ads AI Connectors (mcp.facebook.com/ads, 29 scoped tools, Business OAuth, launched April 29 2026, free in beta) for any ads automation. This is the strongest disproof of any "brand-level" ban: Meta itself sanctions Claude as an ads-management client. Confirmed across GoMarble, Pasqualepillitteri, Digiday.
- Read-only by default; every write behind a human-approval queue.
- Rate-governance in every Meta client: hourly-max polling, sequential per-account processing, exponential backoff on 613 and all errors, hard pause at a self-imposed prudent BUC margin read from the response header. (Treat the "60% BUC" figure as a self-imposed margin, not a Meta-published cliff; Meta publishes the header and the points system, reads = 1 point, writes = 3, but not a 60% threshold.)
- Blast-radius isolation: one Business Manager / ad account boundary per client; never manage client ad accounts under the personal profile that runs experimental automation.

**What's overstated (do not encode as fact).** The "three-tier appeal" with specific percentages (35% in 24h, 3-5 days, 10-15 days) is uncorroborated and conflates the appeal timeline with Meta's Trust Tier scrutiny system. Do not cite those numbers. The Anthropic-subscription-block caveat is stale (reporting indicates a reinstatement "with a catch"); operative advice is unchanged: use the official Anthropic API or Meta's MCP, never pipe a subscription through an agent.

### 2. llm-and-payment-tos (verdict: solid)

**Triggers.** LLM: model generates explicit output (direct Anthropic AUP violation, verbatim-confirmed bullets). Org-level blast radius: a flagged violation can suspend the entire organization (keys keep billing during lockout, banned email cannot view usage, single appeal form, no SLA). Minor-safety tripwire: any sexualized output involving someone under or appearing under 18 (absolute ban, reported to law enforcement). Payments: Stripe reclassifies the business as adult (verbatim restricted list: "Pornography and other mature audience content... designed for the purpose of sexual gratification", "Adult services, including... adult live-chat features"). Chargeback spike. Termination cascade to MATCH/TMF (5-year processor lockout). Fund freeze on suspicion (documented $16,448, 6+ months).

**Mitigations and build rules.**
- Non-explicit by design, enforced by the hard-banned system prompt and the fail-closed pre-send moderation gate. This keeps the bot inside the defensible reading of Anthropic's AUP, which bans generating explicit content, not operating in an adult-adjacent industry.
- Dedicated Anthropic org, separate billing, no shared keys with the agency core (protects Google Ads MCP work and client fulfillment from a flag).
- Provider-abstracted LLM layer: one swap point, prompt portable across Anthropic / OpenAI / Bedrock-hosted open weights. OpenAI is fallback-only for the non-explicit copy; its "adult mode" was paused indefinitely (2026-03-26, confirmed across multiple outlets) and API explicit-unlock needs approval most businesses will not get.
- B2B SaaS billing structure, separate legal entity, high-risk processor on standby, multi-month cash buffer, voluntary-close-only exit policy. Chargeback rate is a survival KPI.

**Caveat to hold.** "Non-explicit by design" is necessary but not a guarantee. Anthropic's AUP bans generating explicit content but is silent on marketing-assistance for adult-adjacent businesses, leaving a discretionary gray zone. Plan for it being interpreted against you.

### 3. prospecting-outreach-safety (verdict: solid)

**Triggers.** Cold DMs to OFM operators who never initiated (confirmed: the single highest-risk DM category, no compliant API path). Volume over the daily caps. Hourly bursts. Identical templated copy at machine speed. Follow/unfollow churn. Any automation in the first 72 hours of a new account. Multiple outreach accounts on the same device/IP. Feeding an outreach login into Apify or any unofficial tool. OF-adjacent solicitation language on the outreach bio.

**Mitigations and build rules.**
- The only true mitigation is shifting toward user-initiated triggers and keeping per-account volume genuinely low. No warming schedule fully de-risks cold DMing at volume (the research's own strategic conclusion, confirmed `solid`).
- Per-account warm-up gate before any prospecting: Week 1 likes/follows/comments, zero DMs; first DMs around day 11 at ~5/day; ramp to ~10-15/day by weeks 3-4. No automation in the first 72 hours. Track warm-up status per account; no account enters rotation until the gate passes. (Numbers transcribed accurately from the shadowphone source, treat as conservative working ceilings, not Meta policy.)
- Conservative volume band: treat ~20-30 cold DMs/day as the ceiling on an aged account, ~5-10/day on a freshly warmed one, ~3-5/hour, with day-to-day variation. These are maxima, not targets.
- Personalize every DM (no two consecutive sends identical, banned at the tooling level). One account per device/IP, accounts staggered at least a week apart, profiles fully completed first. SFW B2B-positioned bio, no onlyfans.com links, no solicitation language. A warmed backup pool sized to survive losing 1-2 accounts.

**Tightening from the verdict.** The first-strike penalty for cold outreach specifically is harsher than the generic ladder: creatorflow reports a 7-day messaging restriction on the first detected wave, 30 days on the second. So the circuit breaker should pause longer than 48-72h for a cold-DM strike, and retire the account on a second strike.

### 4. ig-dm-automation-policy (verdict: partly_real, architecture solid, numbers vendor-sourced)

**Confirmed and load-bearing.** The 24-hour window and user-must-message-first rule (verbatim, Meta docs). AI disclosure requirement (Meta docs + CA/Germany legal note). `HUMAN_AGENT` must be human-applied (long-standing Meta policy). No compliant path for cold first DMs. Unofficial automation is the real ban vector while official-API Business Partners survived. Tag deprecation is real.

**Demoted to tunable operating conventions (do NOT cite as Meta policy).** The "200 automated DMs/hr, cut from 5,000 in 2026" figure has no official Meta page and sources disagree on timeline (CreatorFlow vs SumGenius). Meta's documented limits are per-second, not per-hour. The "1 DM/user/24h on triggers" cap is uncorroborated and partly contradicted (spurnow: effectively unlimited within the 24h window). The April 27 2026 date conflicts with the Feb 9 2026 ManyChat timeline. The "browser bots are hard bans" certainty exceeds the evidence.

**Build rules.** Implement the structural rate-limiter (cap at a conservative self-imposed ceiling, pace under whatever the real limit is, alert at 80%), but mark the numbers as tunable constants to re-verify in the live Graph API dashboard before launch, not as quotable Meta limits. Everything architectural (Graph API only, user-initiated only, 24h window in code, human-only HUMAN_AGENT) ships as written.

### 5. ig-creator-link-practices (verdict: partly_real)

**Confirmed.** Don't use Linktree for an OF account, use an adult-permissive router (Beacons content-warning toggle / AllMyLinks). Keep the actual OF link out of public fields. Deliver it through a hub, not a raw onlyfans.com URL. AI disclosure. The defensive doctrine (clean indirect public surface, link delivered only in-window after user initiation, route through an adult-permissive hub or custom domain) is sound regardless of mechanism.

**The core thesis is a VENDOR ASSERTION, not proven.** The load-bearing claim that "private DMs are not scanned by the public URL-moderation pipeline the same way" comes only from inro.social, an automation vendor, with zero Meta documentation. Treat as a plausible heuristic, not established fact. Do not build the model on the assumption that in-DM links are scan-proof; build it on keeping the public surface clean and the link indirect because that is cheap and right regardless.

**Overstated history.** The Linktree "multiple waves, explicitly bans OF links" story is embellished. The Jan 2022 event banned a small number of accounts and the CEO said it was for illegal in-person sexual services, explicitly not for OF links. The current-state risk (2026 TOS bars adult content) is real; the dramatic origin story is not.

**Build rules.** Hub config requires an adult-permissive router, rejects `linktr.ee`. Maintain a SFW safety ratio on the hub (several clean links per adult link). Keep hub copy suggestive, not graphic. Custom domain is the only fully durable hedge against third-party deplatforming, push creators toward yourname.com where possible.

### 6. multi-account-isolation (verdict: partly_real, spine confirmed, several numbers invented)

**Confirmed and hardest.** Mosseri on record (The Mirror, April 25 2026): OF creators are removed for promoting/soliciting, NOT for being an OF creator ("You can't promote, you can't solicit, so you can certainly be on Instagram"). ManyChat is an official Meta Business Partner confined to the 24h window, cannot cold-DM by API design. The ~200 automated DMs/hr/account ceiling IS real and effectively official (Meta cut it from 5,000 to 200/hr in October 2024, per-account, shared across all connected tools), which reframes "multi-tool stacking" correctly as a shared-rate-limit collision, not a mystical "Meta counts your apps" signal. Bright Data precedent. Oversight Board due-process gaps.

**Strip these invented numbers (do not hard-code).** "Contact-book overlap ~20%+" as a flag threshold (no source, invented precision). "~80% ban rate in first month" (vendor folklore). "~3 linked accounts cascade threshold" and "rolling ~90-day IP log" (pseudo-precise, no Meta basis). Keep the qualitative principles, drop the false numbers. Reframe "Meta blocked every known datacenter ASN (instant ban)" from absolutes to "cloud ASNs are heavily flagged."

**Strategic flag (the most important line in this surface).** The entire heavy gray-hat stack (mobile proxies, anti-detect browsers, SIM farms, isolation registry) only applies if we own a farmed fleet. For Hoexa as scoped, ManyChat on the creator's existing aged account on her device and SIM, roughly 90% of the ban-risk surface is not ours to carry. Build the SOP as hygiene + warm-up gate + public-surface rules. Do NOT let this dossier pull the product toward building an account farm; that is scope creep into the exact catastrophic surface the safe path avoids.

## Founder Fears, Checked

- **"Instagram is aggressively banning OF creators and link practices in 2026."** PARTLY. Confirmed that Instagram suspends accounts and shadowbans over HOW creators promote (raw onlyfans.com links, solicitation language, explicit content, NSFW hashtags), and suspended 100+ sexual-health/LGBTQ accounts in April 2026 (Attitude, Advocate). But Mosseri is on record that creators are NOT banned for existing as OF creators, only for promoting/soliciting (The Mirror, April 25 2026). The link-scanning mechanic that "in-DM links escape scanning" is an unproven vendor claim (inro.social), so the fear is real in direction, overstated in the specific scan-proof mechanism.

- **"Doing shady shit with bots could get the whole business shut down overnight."** CONFIRMED for the wrong kind of bots. Unofficial automation (browser bots, password tools, scrapers, cold-DM blasting) is the genuine fastest path to a permanent ban (creatorflow, spurnow, confirmed across the DM-automation and prospecting verdicts). OVERSTATED for the right kind: ManyChat on the official Graph API, user-initiated only, is a Meta Business Partner that survived the ban wave (confirmed). The fear is correct; the fix is staying on sanctioned rails, not abandoning automation.

- **"Meta is reportedly banning Facebook/IG/ads accounts associated with AI tools."** OVERSTATED as stated, CONFIRMED when reframed. Enforcement is behavior-based, not brand/tool-based (Supermetrics, Zentric, Blend, all `solid`). The "Claude Code got my account banned" case was caused by ungated write access plus inhuman cadence plus retries, not the Anthropic name. The strongest disproof: Meta itself launched an official MCP sanctioning Claude as an ads-management client on April 29 2026 (Digiday, GoMarble). The risk is real but the cause is HOW the agent connects, not THAT it is AI.

## What This Changes in the Build

**find_ofm_managers / prospecting pipeline.**
- Apify scraping moves to logged-out-only, on its own proxies and IPs, fully decoupled from any outreach or creator login. Add a hard rule: no outreach login is ever entered into Apify. Scraping output feeds a separate list store; it never auto-DMs.
- Separation of concerns enforced as three isolated layers with no shared credentials: scraping, lead store, messaging accounts. A scraping block can never cascade into an account ban.
- Outreach accounts get the warm-up state machine (zero DMs week 1, first DMs ~day 11, no automation first 72h) and SFW B2B-positioned profiles. Build the volume circuit breaker to pause longer than 72h on a cold-DM strike (7-day first-wave penalty is the realistic figure) and retire on a second strike.
- Strategic shift: engineer toward user-initiated triggers (operators reply to a story, comment a keyword, DM from a content post) over truly cold blasts wherever the funnel allows. Cold-at-volume cannot be fully de-risked.

**ManyChat deploy.**
- User-initiated triggers only, hard-coded as a non-bypassable precondition. 24h-window enforcement with last-inbound timestamps. AI disclosure node and 18+ age gate baked into Phase 0 as non-removable. Pre-send fail-closed content filter on every outbound message.
- Link-config layer never stores or emits a raw onlyfans.com URL; only the configured adult-permissive hub. Validation rejects `linktr.ee`.
- Rate-limiter ships, but its numbers (the ~200/hr ceiling, any per-user trigger cap) are tagged as tunable constants to re-verify in the live Graph API dashboard before launch, not encoded as quotable Meta policy. Confirm no deprecated message tags remain.

**Multi-account architecture.**
- Default to running on each creator's existing aged real account on her own device/SIM. Farm fresh accounts only as a fallback, routed through full warm-up first. Do NOT build a proxy/anti-detect/SIM-farm fleet; that is the catastrophic surface we are avoiding.
- One creator = one isolated stack (IG account, FB Page, hub, custom-field namespace), no shared hub domain across creators. Per-account kill switch and health monitor. Build for account loss as a normal event with content/account backups.

**LLM and money rail.**
- Hoexa LLM calls run on a dedicated isolated Anthropic org, separate billing, provider-abstracted with one swap point. System prompt carries the verbatim AUP-mirrored explicit-content ban. Any Meta ads automation routes through the official Ads MCP with human-gated writes and read-only default.
- Hoexa operates under a separate legal entity / EIN / bank / Stripe descriptor, billed as B2B agency services to OFM agencies. One high-risk processor kept warm. Multi-month cash reserve outside the primary processor. Voluntary-close-only exit policy to dodge MATCH.

## Open Risks / Monitoring

- **Re-verify the soft numbers in the live Graph API dashboard before launch.** The ~200 DMs/hr cap, any per-user trigger cap, and the warm-up day counts are vendor-corroborated conventions, not published Meta policy. Pace under them; do not cite them as ground truth.
- **Re-confirm the April 27 2026 tag-deprecation date against Meta's live changelog.** It conflicts with the Feb 9 2026 ManyChat timeline. The deprecation is real; the exact date is not reliably pinned.
- **Link-router policies change overnight (Linktree precedent).** Re-verify Beacons/AllMyLinks adult-friendly status periodically. The only durable hedge is the creator's own custom domain.
- **Anthropic AUP gray zone on adult-adjacent marketing assistance.** The AUP is silent on it. Monitor for any AUP update that narrows the "non-explicit generation" defense. Keep the dedicated-org isolation regardless.
- **Stripe / processor reclassification risk is continuous, not one-time.** A website change, content drift, or dispute spike can trigger review at any point. Keep the descriptor and billed entity clean and the backup processor warm.
- **Meta enforcement is AI-driven and error-prone with weak appeals (Oversight Board, June 4 2026).** Even compliant accounts get caught in ban waves. Treat account loss as routine; maintain backups and a one-appeal SOP.
- **OpenAI "adult mode" status and Anthropic third-party-agent access both shifted in 2026 and may shift again.** Keep the provider abstraction so a policy flip is an hours-long swap, not a rebuild.
- **V2 on-platform OF chatter stays gated on legal review** (OF TOS bans on-platform bots). The IG front end is policy-safe; the on-platform layer is not. Do not build it without a lawyer or an official OF chatbot API.
