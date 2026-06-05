# Phase 4: Productize and sell

Status: ⬜ Not started · gated on Harvey's pilot creator hitting ≥5 attributable subs in week 1
Owner: EZJ + Claudia
Output: `../deliverables/outreach_kit.md`, first non-Harvey OFM closed

## Step 4.1: Wait for proof from Harvey ✅ Locked · ⬜ Not started

Don't open Phase 4 until the Harvey pilot creator has produced:
- ≥5 attributable OF subs in week 1, OR
- ≥10 attributable OF subs in the first 30 days

These thresholds came from the approved plan's verification section. Either threshold proves the bot converts. Either threshold becomes the case-study number we lead outbound with.

If both thresholds miss: re-enter Phase 1 with prompt iteration. Don't open outbound on weak proof.

## Step 4.2: Capture the case study ✅ Locked · ⬜ Not started

Once we hit a threshold:
1. **Loom**: EZJ records a 60-90 second screen-share showing the bot in action on Harvey's creator (DMs blurred for the fan, but the conversion arc visible).
2. **Numbers**: dollar-attributable revenue, sub count, conversation count, conversion rate.
3. **Harvey quote**: get him on camera or in writing endorsing the product (founder-rate trade includes case-study rights).

Output: case study slot in `../deliverables/offer_doc.md` filled in.

## Step 4.3: Build the cold outreach kit ✅ Locked · ⬜ Not started

Output: `../deliverables/outreach_kit.md`. Three artifacts:

1. **OFM lead list.** Sources:
   - IG search for "OFM" / "OnlyFans management" / "creator agency" in bio
   - Twitter/X same
   - OFM Discord servers (manual scrape, members who post "we manage X creators")
   - Apollo + Apify if any structured B2B databases exist (mostly won't)
   - Referrals from Harvey (peer OFMs he knows)
2. **DM template.** 3-message warm-cold DM cadence. Loom-personalized opener, value pitch, case study + CTA.
3. **Cal.com page.** Dedicated "OFM IG DM Audit" 15-min Cal.com page with the offer doc + Loom on the booking confirmation.

## Step 4.4: Run outbound ✅ Locked · ⬜ Not started

Target: 50 personalized Looms/DMs to OFMs in the first 2 weeks. Track:
- Reply rate
- Booked-call rate
- Closed-pilot rate

Goal: 2 closed non-Harvey OFMs in 30 days. Each at 3 creators = 6 creators × ~$1.5k MRR equivalent = $9k MRR added.

## Step 4.5: Standardize the per-creator delivery sprint ✅ Locked · ⬜ Not started

Document the 7-day delivery sprint as a repeatable SOP:

| Day | Task |
|-----|------|
| 1 | Kickoff call, knowledge base doc started, ManyChat creator invite sent |
| 2 | Knowledge base doc completed by creator (voice samples, sub price, hard NOs) |
| 3 | n8n workflow cloned + creator-specific config, ManyChat custom fields built |
| 4 | ManyChat triggers and Send Flow wired, knowledge base linked into n8n |
| 5 | End-to-end test on burner IG, EZJ iterates prompt for creator's voice |
| 6 | Creator reviews 10 sample conversations, sign-off on tone |
| 7 | Go live, EZJ monitors first 24 hours |

Output: SOP slotted into `../deliverables/delivery_sprint_sop.md`.

## Verification (success looks like)

- [ ] Harvey pilot has ≥10 attributable subs in 30 days
- [ ] Case study captured (Loom + numbers + quote)
- [ ] Outreach kit shipped
- [ ] 2 closed non-Harvey OFMs in 30 days from outbound start
- [ ] Per-creator delivery sprint SOP documented and used at least once
