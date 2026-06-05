# Phase 3: Pricing and offer (`/hormozi pricing`)

Status: ⬜ Not started · gated on Phase 2 pilot being live
Owner: EZJ + Claudia (via the `hormozi-pricing` skill)
Output: `../deliverables/offer_doc.md`

## Step 3.1: Run `/hormozi pricing` ✅ Locked · ⬜ Not started

Invoke the `hormozi-pricing` skill with these inputs (paste this brief in when prompted):

```
We are pricing an AI-driven Instagram DM conversion service for OnlyFans
Management agencies (OFMs).

What it does: converts a creator's IG followers into paid OF subs via
automated, on-brand DMs. Replaces no one (the IG layer is currently un-staffed
at most OFMs). Layers on top of existing chatter teams who do the on-platform
work.

Anchors:
- Filipino chatter teams cost OFMs ~$1.5k-$3k per creator per month for
  on-platform work
- New OF sub at $9-$30/mo retains 2-4 months on average ($18-$120 LTV per sub)
- One extra sub per creator per day = $300-$1.2k MRR uplift per creator

ICP: OFM agencies with 5-30 creators, each $5k-$50k/mo on OF, 5k-100k IG.

Our cost basis per creator:
- Initial setup (ManyChat, knowledge base doc, prompt customization): ~6 hours
- Ongoing monitoring/iteration: ~2 hours/week first month, ~30min/week steady state
- Inference: ~$10-$50/mo per creator (model usage)

Anchor we need to break: Harvey's first project was $700. We need to reset
to a serious anchor for this product.

Pilot client: Harvey (Monetize.me, 12 creators). We need a founder rate for
him in exchange for case study rights.

Design:
1. Setup fee (per creator)
2. Performance share % on attributable new OF subs
3. Founder rate for Harvey
4. RAISE framework for next price increase
5. Grandfathering rules
```

The skill returns: setup fee, performance share %, founder rate, RAISE timeline, grandfathering.

## Step 3.2: Pick the attribution mechanism ✅ Locked · ⬜ Not started

Performance share requires attribution. Options:

| Mechanism | How it works | Pros | Cons |
|-----------|--------------|------|------|
| UTM on OF sub link | Each conversation hands out a unique UTM-tagged OF link, OF dashboard shows source | Standard, OF-native | UTMs can be stripped, harder to audit |
| ManyChat tag + manual reconciliation | Bot tags `OF_Link_Pitched` then `Subscribed`, cross-ref with OFM's OF dashboard at month-end | Auditable, no UTM dep | Manual reconciliation each month |
| OF promo code per pilot creator | Custom promo code only available via the bot | Cleanest attribution | OF promo codes are limited and creator may not want a dedicated one |

Recommendation: ManyChat tag + manual monthly reconciliation for V1. Switch to UTM once we have 5+ creators and need to automate.

## Step 3.3: Write the offer doc ✅ Locked · ⬜ Not started

Output: `../deliverables/offer_doc.md`. Client-facing one-pager. Sections:

1. **The problem.** OFMs are leaving IG sub revenue on the table because human chatters can't work IG DMs at scale.
2. **The solution.** AI-driven IG DM conversion that impersonates the creator (or her assistant) and converts followers into paid OF subs.
3. **What you get.** Per-creator deployment, knowledge base doc, ongoing optimization, attribution dashboard.
4. **What you pay.** Setup fee + performance share. Founder rate for early adopters.
5. **The proof.** Once Harvey's pilot creator has 30 days of data, slot the numbers in here. Until then, leave a placeholder.
6. **The fine print.** Platform-safety disclosures. No explicit content in DMs. ManyChat-only opt-in flows. AI disclosure on the standard triggers. Persona transparency to the buyer.
7. **Next step.** Cal.com booking link or direct Telegram.

## Step 3.4: Pitch Harvey on the locked pricing ✅ Locked · ⬜ Not started

Once the offer doc exists, pitch Harvey on the founder rate. Frame: "you piloted V1 for us, you get permanent founder pricing on your first 3 creators in exchange for case study rights." This locks Harvey as a long-term anchor and gives us social proof for outbound.

## Verification before Phase 4 begins

- [ ] `/hormozi pricing` run, output captured in `../deliverables/pricing_output.md`
- [ ] Attribution mechanism picked and documented
- [ ] Offer doc written, reviewed by EZJ
- [ ] Harvey pitched on founder rate, response captured
- [ ] Pilot creator has ≥7 days of live data
