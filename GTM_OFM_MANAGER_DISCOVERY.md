<!-- Generated 2026-06-13 by the ofm-manager-discovery research workflow. 7 discovery vectors, each adversarially verified. Living doc. -->

# OFM Manager Discovery Playbook

## TL;DR

Five of six vectors verified solid, one verified partly_real. The single best automatable path is **bio-handle-patterns**: it is the only vector rated `direct` handle yield AND `fully` automatable AND verdict `solid`, because Google indexes every Instagram page title as "Display Name (@handle) Instagram photos and videos", so you regex the handle straight out of the SERP with no login or bio scrape. Everything else (agency-site, LinkedIn, X, directories, chatter-boards) yields a brand NAME or person NAME first and needs a second name-to-IG bridge, so they are sourcing layers that feed the same enrichment step. The recurring hard truth across all six verdicts: you almost always land the agency BRAND inbox, not the human decision-maker, and the human-handle step is the manual, error-prone part that needs an LLM-judge gate. Creator-reverse-lookup failed on our actual fitness list (zero agency signals leaked), so it is a filter, not an engine.

## Ranked Vectors

| Vector | Yields handles | Automatable | Confidence | Verdict | One-line why |
|---|---|---|---|---|---|
| bio-handle-patterns | direct | fully | high | solid | Only vector that pulls the literal @handle out of the Google SERP title with no login. Highest yield. |
| agency-site-to-ig | direct | partial | high | solid | Tier-A bio pages (TDM) link the operator's personal IG directly. Most sites are anonymous, so volume is thin but quality is high. |
| linkedin-to-ig | indirect | partial | medium | solid | `site:linkedin.com/company "OnlyFans Management Agency"` returns real agencies with a clean LinkedIn auto-suffix headline. Reaches professionalized agencies, misses solo operators. |
| directories-communities | indirect | partial | high | solid | Listicles plus Telegram/Discord rosters are the densest top-of-funnel sourcing pool. Yields brand names, needs the bridge step. |
| chatter-job-boards | indirect | partial | high | partly_real | ofmjobs.com / ofmjob.com attach Telegram/Discord handles on-post. One fabricated name-to-IG mapping (Besa) proves the bridge is error-prone. |
| creator-reverse-lookup | indirect | partial | low | solid | Honest self-assessment: failed on our real fitness creators (zero agency signal). Use as a filter, then invert to scraping agency accounts directly. |

## The Build

A `find_ofm_managers` pipeline. Two stages: cheap SERP-native handle harvesting (Stage 1), then name-to-handle bridging for the sourcing vectors (Stage 2). Everything funnels through one scorer and one LLM-judge gate.

**Inputs**
- A rotating query matrix (platform anchor x site filter x CTA token), seeded and re-seeded each run.
- Optional seed list of confirmed agency handles to expand via follow-graph.
- The existing `leads/` creator CSVs (for de-dupe and the reverse-lookup filter).

**Steps**
1. **Stage 1, bio-handle-patterns (primary, fully automatable).** Build the query matrix: anchor ("OnlyFans management agency" OR "OFM" OR "creator management" OR "talent management") x `site:instagram.com` x a rotating CTA token ("DM to apply" OR "now signing" OR "Apply below" OR "Top 1% creators"). Run through a SERP source (Google `site:instagram.com`, plus the `tavily-search` and `x-search` skills for cross-platform). Parse the handle straight out of each result title with `\(@([A-Za-z0-9._]+)\)`. No bio scrape, no login. The seed query `ONLYFANS MANAGEMENT AGENCY instagram` (caps mimics how operators title their bios) is independently confirmed to return a dense operator cluster (@lounasmodels, @thelushmgmt, @nexomanagement, @klimagency, @unfiltered_management, @atlas.ofm, @heliomanagement).
2. **Stage 1 scorer.** For each hit: +1 management keyword in display name, +1 convention suffix in handle (.agency / .mgmt / .ofm / _ofm / management / agencyy), +1 recruiting CTA token in the SERP snippet. Keep hits scoring 2+.
3. **Stage 2, sourcing vectors (partial automation).** Run in parallel, all feeding the same bridge:
   - LinkedIn: Google-dork `site:linkedin.com/company "OnlyFans Management Agency"` and `site:linkedin.com/in "OnlyFans management" founder OR CEO`. Never use bare "OFM" (collides with OFM Finance / Capital / Engineering). Extract agency brand from the LinkedIn auto-suffix headline "Name - Agency | Onlyfans Management Agency".
   - Directories: scrape the listicles (sidesmedia.com/onlyfans-management-agency, xcreatormgmt.com/blog/best-onlyfans-agencies, dolphin-anty.com/blog/en/best-onlyfans-agencies). Each yields 8 to 20 named agencies. Filter out sub-buying services (UseViral, SidesMedia, BuyFansSubs, Growthoid) which the listicles mix in.
   - Chatter boards: crawl ofmjobs.com/find-jobs and ofmjob.com (these attach Telegram/Discord handles directly on the listing), plus WeWorkRemotely / smartremotejobs.com where the employer is a clean registered name (e.g. "Bunny Agency LLC").
   - Agency sites: from the directory domains, crawl /about, /the-agency, /meet-the-team, /careers for person names and the Tier-A `domain.com/firstname-lastname/` bio-page pattern that links personal IG directly (this is where @liamtdm, @camerontdm came from on tdmmanagement.com).
4. **Stage 2 bridge (name to IG).** For each agency brand name, query `"<agency name>" OnlyFans management instagram` and regex `instagram.com/<handle>` out of the SERP and the site footer. Verified bridges: E Management Agency to @emanagementagency, Model Starz to @modelstarzmanagement, Hush to @hushfameagency, Bunny Agency to @onlybunnyagency.
5. **LLM-judge gate (mandatory, load-bearing).** Before any handle enters the output, an LLM pass confirms the IG bio reads as an OFM operator (sells management/recruiting/chatting/scaling), NOT a model paywall and NOT a name collision. This gate exists because the chatter-board vector produced a confirmed fabricated mapping (Besa Group to @besa.groupuk, which is actually a study-abroad agency). Never trust a name-to-IG bridge without it.
6. **Follow-graph expansion.** Off confirmed accounts, pull "Suggested for you" / followed-by and re-run the scorer. OFM operators heavily follow and tag each other.
7. **Human-mapping step (optional, warm outreach).** Where a founder name appears in bio or a tagged personal account ("run by @name"), map brand to human so outreach hits the person, not the brand inbox.
8. **De-dupe** against existing `leads/` and prior runs. Write output.

**Tools / Apify actors**
- SERP: Google `site:` dorks, `tavily-search` skill, `x-search` skill (Grok) for X (x.com is JS/bot-walled to WebFetch, returns 402).
- IG profile data (bio, external_url, link-in-bio, tagged tab): **Apify Instagram Profile Scraper / Instagram Scraper** (authenticated). Logged-out instagram.com returns only meta tags, confirmed across multiple verdicts. Use rotation, expect partial pulls, accept the Meta TOS/ban risk.
- LinkedIn employee enumeration: **Apify `harvestapi/linkedin-company-employees`** (cookieless, ~$1.50/1k profiles, confirmed real) or PhantomBuster LinkedIn Company Employees Export.
- Telegram member/roster mining: **telethon** against public groups (t.me/ofagencytalk = 1,410 members admin @adrianmeissner; TDM Business OFM t.me/+VTItdzrudoU2YTM0 = 8,358 members; @onlyfanschatterandhiringhub). Gray-area on TOS, rate-limits/bans the scraping account.
- LLM-judge: any cheap model (Haiku class) for the bio-reads-as-operator pass.

**Expected output columns**
`agency_name | ig_handle | yields_target (brand|human) | operator_name | linkedin_url | website | telegram_handle | source_vector | source_url | score | follower_count_est | judge_verdict (operator|model|collision|unsure)`

## Detection Signals

Encode these directly into the scorer and the LLM-judge prompt.

**Display name regex (the agency signal):** `(?i)(onlyfans|of)\s*(management|mgmt|talent|creator)\s*(agency)?`. Confirmed live titles: "OnlyFans Management Agency | Lush MGMT", "ONLYFANS MANAGEMENT AGENCY" (magxagency, luxury_agencyy_), "Sapphire OnlyFans Management", "OF Management Agency" (papik.ofm), "Ofinity OFM Agency", "OnlyFans Management Company" (alluringmgt), "The Official OFM Agency Organization" (profmax.co).

**Handle suffix regex (the convention):** `(?i)(\.agency|\.mgmt|\.ofm|_ofm|_mgmt|management|agencyy?_?)$`. Confirmed live: .agency, .mgmt, .ofm, _ofm, sophiamanagementagency, luxury_agencyy_.

**Handle extraction from SERP title:** `\(@([A-Za-z0-9._]+)\)` against the Google-indexed "Display Name (@handle) Instagram photos and videos" pattern. This is the load-bearing automation regex.

**Bio CTA tokens (recruiting funnel):** "Apply below", "Apply to work with us", "DM to apply", "now signing", "now accepting", "accepting applications", "apply via link", "DM for management/collabs/promo".

**Status / proof tokens:** "Top 1% creators", "Top 0.01%", "$10M+ in creator revenue", "trusted by 60+ creators", "Multiple Top 1% Creators".

**Service-triad tokens:** "promote, manage and scale", "Growth Branding Revenue Scaling", "Growth strategies & content management", "content, DM management, analytics".

**LinkedIn auto-suffix pattern (the bridge tell):** personal headline "Name - <Agency> | Onlyfans Management Agency" exposes both person and agency. Company page title contains "OnlyFans Management Agency".

**Euphemistic OFM-vs-generic-talent language:** "customer retention", "engagement", "media assistants", "chat operators", "per-message commission", "night shift / 24/7 coverage", "PPV / upsell". Hiring Philippines / Serbia / Eastern-Europe chatters flags a real operating agency over a course seller.

**Site nav paths (agency-site vector):** /about-us, /the-agency, /meet-the-team, /our-team, /careers, /onlyfans-agency-jobs. Tier-A bio-page URL pattern `domain.com/firstname-lastname/` is the strongest signal that a personal IG is linked.

**Visual signals (need the Apify scraper):** agency watermark / end-card logo on promo reels, same studio geotag or backdrop across unrelated creators, a tagged tab full of creator faces, a shared/identical link-in-bio template (same Beacons/Linktree theme) reused verbatim across multiple creators.

**Premium emoji cluster (low count, status markers):** diamond, star, rocket, heart, crown in display name or bio.

**Link-in-bio router:** Linktree / branded short link / Typeform-or-Exclu application form routing to a creator intake. This is the funnel that separates a true operator from a model.

**Negative signals (exclude, to keep models and collisions out):**
- Bio contains "NO AGENCIES" or a single OF/Fansly paywall link rather than an application funnel (this is a creator, not an operator).
- Name-collision risk: common brand words ("Bunny", "Besa") map to unrelated personal or non-OFM accounts. The Besa Group to @besa.groupuk mapping was a confirmed false positive (study-abroad agency). Always run the judge gate.
- Aggregator / "best agencies" listicle pages and sub-buying services (UseViral, SidesMedia, BuyFansSubs, Growthoid) are not operators.

## Creator Reverse-Lookup

**What our real fitness creators leak: effectively nothing.** This is the honest, verified finding. Our scraped OF creators (e.g. @sarahfrenchonline, @fitwithbrittanie, @frankenstein.legs) carry zero agency signals in the data we hold. Their bios have no link-in-bio aggregators and no "managed by" text. @lillydreamz is explicitly independent ("no i don't want to join your agency"). A few (almlten, jennyleevip, mirandajohnson) show managed-DM tells like "I read all" / "chat with me daily", but those only indicate a chatter team exists, they do NOT identify a findable agency. Mid and low-tier creators (which is our whole list) are the least likely to leak a manager, because agencies hide the relationship on purpose. Reversing creator to manager yields, at best, a name, rarely a clean handle.

**So do not run this as a primary engine. Run it as a filter, then invert.**
1. Use the existing Apify IG scraper to pull each creator's bio, external_url, link-in-bio aggregator (allmylinks is most fetch-friendly; linktr.ee and beacons.ai 403/404 to bots, route them through Apify too), and the "tagged" tab.
2. Regex bios and aggregators for "managed by", "promo by", "mgmt", "management", "agency", "represented by", "booking", "business inquiries", and any non-personal @handle that recurs.
3. **The actual yield move: cross-reference.** Collect every tagged account and recurring @mention across the whole creator list. Any single non-creator account tagged on or cross-promoting 3+ creators is a probable agency hub. Then INVERT: scrape that hub's tagged tab to enumerate its full roster, and scrape its bio for the operator name. This is how the agency handles in the data (@lounasmodels, @thelushmgmt, @modelstarzmanagement, @fem.management.global, @emanagementagency, @luxe.visage.models, @onlynationagency, @gavinmagoonofm) were actually found, by inverting to the agency side, not by reversing from creators.
4. Score each creator agency_signal yes/no/weak. Route "no signal" (the majority) to the bio-handle and directory vectors. Route "signal" creators' inferred agency into the agency-side enumeration. Bonus tell: @gavinmagoonofm maps to Model Starz, which is exactly the hub-enumeration logic working.

To scale it: this only produces throughput on top-tier creators who get publicly featured by their agency. For our mid-tier fitness list, the reverse-lookup is a low-yield supplement. Put the compute into Stage 1 (bio-handle) and the directory/board sourcing, and use reverse-lookup to catch the occasional signal-leaking creator and pivot to agency scraping.

## Split-Test Plan

Two outreach arms. Both stay inside the Hard Constraints (no cold-DM outbound on the bot itself; this is manual prospecting outreach to a B2B buyer, not the product running).

**Arm A: DM the creator directly**
- Target: the OF creator's own IG (the accounts already in `leads/`).
- Conversion reality: low for selling Hoexa. Most are independent or already have a chatter team, and the buyer of a DM-to-sub bot is rarely the creator herself. Useful mainly to surface "who manages you?" and route to the operator. Treat Arm A largely as a referral/intel arm, not a close arm.
- Message angle: creator-pain framing. "Are you converting your IG followers into subs, or leaving them in the DMs?" Soft, then ask who handles their DMs / management so you can reach the operator.

**Arm B: DM the agency operator**
- Target: the agency brand IG (or the human operator handle where mapped). This is the real buyer.
- Conversion reality: higher intent, but the brand inbox is often a VA or recruiter, not the decision-maker. The public CTA on these accounts ("apply below", "now signing") is aimed at recruiting MODELS, so a generic inbound reads as spam. You must reframe to the operator's pain or it dies.
- Message angle: operator-pain framing. Lead with chatter cost and DM-to-sub conversion. "You're paying a chatting team to convert IG followers into subs. We automate the IG DM front-end so your chatters only touch warm, paywall-ready leads. Cuts chatter hours, lifts conversion." Reframe away from "apply" toward "scale your roster's revenue per follower".

**Attribution (how to know which arm wins)**
- Tag every prospect at source with `source_vector` and `arm` (A or B) in the output sheet.
- Use a distinct cal.com booking link or a distinct UTM/tracking param per arm so booked calls attribute cleanly to A or B.
- Primary metric: **booked qualified calls per 100 DMs sent**, split by arm. Secondary: reply rate, positive-reply rate, and "routed-to-operator" rate for Arm A (since A's real job is to produce an operator lead, count that as an A conversion even though the close happens in B).
- Decision rule: whichever arm produces more booked calls per 100 DMs after a fixed sample wins the budget. Expectation going in, and state it so the test is honest: Arm B closes, Arm A feeds B. The likely real winner is a hybrid where A's referrals become B's warm opens.

## Immediate Next Actions

- Build Stage 1 first. Stand up the bio-handle SERP harvester with the query matrix and the `\(@([A-Za-z0-9._]+)\)` regex. It is fully automatable, solid, and the only direct-handle vector. Ship this before anything else.
- Run the confirmed seed query `ONLYFANS MANAGEMENT AGENCY instagram` and the CTA-token rotation today to produce a first handle batch, scored 2+, into the output sheet.
- Wire the LLM-judge gate (Haiku) before any handle is written out. This is non-negotiable given the Besa false-positive. No handle ships without an operator/model/collision verdict.
- Stand up the name-to-IG bridge as a shared function, then point the four sourcing vectors (LinkedIn dorks, listicle scrape, ofmjobs/ofmjob crawl, agency-site /team crawl) at it in parallel.
- Provision the Apify Instagram scraper (with proxy rotation) for follow-graph expansion and the reverse-lookup invert step. Budget for partial pulls and TOS risk.
- Set up the two-arm split test with distinct cal.com links and `source_vector`/`arm` tagging in the sheet before sending a single DM, so attribution is clean from message one.

## Open Questions / Manual Spikes Needed

- **Brand-to-human mapping at scale.** Every vector lands the brand inbox; the human operator handle is the manual, unproven step. Spike: take 20 confirmed agency handles and measure how many resolve to a reachable personal operator IG and by what method (bio name, tagged account, LinkedIn cross-ref). If the hit rate is low, accept brand-inbox outreach as the default.
- **Apify IG scraper ban rate.** The follow-graph and reverse-lookup steps depend on authenticated scraping that carries real Meta ban risk. Spike a small run with a burner session and rotation, measure how many handles you pull before throttling.
- **Telegram member mining viability.** t.me/ofagencytalk and TDM Business OFM are the densest operator rosters but telethon scraping can ban the account and member-to-IG conversion is lossy/pseudonymous. Spike one public group, measure the member-to-IG conversion rate before building it in.
- **X-to-IG username-reuse rate.** The cheap X-to-IG hop assumes the same handle on both platforms. This was the one load-bearing automation claim no verdict could test (IG is JS-walled). Spike: take 20 confirmed OFM X handles, check same-handle existence on IG, get a real reuse percentage.
- **Bridge accuracy after the judge gate.** Measure the false-positive rate of the name-to-IG bridge (Besa-style collisions) on a 30-name sample to set how much to trust it and whether a human second-check is needed above the LLM judge.
- **Follower count sourcing.** Counts are behind the login wall and only soft-estimated. Decide whether follower count matters enough to spend Apify calls on, given the verdict that follower count is a weak revenue proxy and funnel quality scores better.
