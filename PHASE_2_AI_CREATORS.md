# Phase 2: We Are The Creator

End-to-end AI-generated OF creators. We own the persona, the content, the IG, the OF, and the DMs. Bella + Maya are the conversation layer; we build the visual and growth layers around them.

This is the moat. Phase 1 (Bella-as-a-service) pays the bills while we build this in parallel.

---

## What we're actually building

A productized AI creator. Each persona has:

| Layer | What | How |
|---|---|---|
| **Identity** | Consistent face/body/style across all content | Flux LoRA trained on a custom synthetic base, or Higgsfield / Pebble / Replicate consistent character API |
| **IG content** | 3-5 posts/week + daily stories | Generated images + AI captions in her voice |
| **OF content** | Photo sets, short videos, custom requests | Generated content behind paywall (still policy compliant, no deepfake of real people) |
| **IG DMs (free)** | Convert followers to OF subs | Bella (already built) |
| **OF chats (paid)** | Upsell PPV, sexting, custom requests | Maya (V2, planned) |
| **Growth** | Get followers to the IG | Mix of organic + paid + cross-promo |
| **Ops** | Schedule content, monitor, intervene | Internal dashboard, semi-automated |

The persona is a **product**, not a personality. We can run 1, 10, 50 in parallel once the pipeline works.

---

## The build pipeline (per persona, repeatable)

### Stage 1: Persona definition (1 day per persona)

- Name, age, location, niche, aesthetic
- Voice DNA (already covered by Bella's knowledge base doc template at `deliverables/creator_knowledge_base_template.md`)
- Visual reference set: 5-10 anchor images defining the look
- 3-5 content pillars (lifestyle, fitness, alt, photoshoot, etc.)
- Hard NOs and persona boundaries
- Sub price + custom-content pricing tiers
- Backstory (where she's from, what she's into, her vibe) — feeds Bella's conversation depth

Output: extended version of the `creator_knowledge_base_template.md` we already use for Phase 1. Same structure, just for an AI persona.

### Stage 2: Visual asset generation (3-5 days per persona)

- **Image gen pipeline:** Flux 1.1 Pro (or whatever's current SOTA) with custom LoRA for consistency
- **Bootstrap photo set:** 50-100 IG-safe photos covering lifestyle, gym, photoshoot, cafe, beach, etc.
- **Paywall photo set:** 200-500 OF-safe photos (suggestive, on-platform compliant, no explicit ban categories)
- **Video clips:** 20-50 short videos generated via Sora 2 / Veo 3 / Runway / KlingAI, person LoRA applied
- **Per-week refresh:** weekly batch of 30-50 new images + 5-10 videos, automated via n8n

**Quality bar:** has to be indistinguishable from a real creator's IG. If it screams AI, it's dead on arrival. Time investment up front is what makes this work.

### Stage 3: IG account warm-up (4-6 weeks per persona)

- Create IG account, convert to Creator profile, connect FB page
- Soft-launch with 30-50 backdated posts (don't post all at once)
- Slow follower growth: 50-200 organic + paid follows/day for first month
- Engagement automation: ManyChat for IG comments + DMs from day 1
- Cross-post to TikTok and Twitter to seed multi-platform discoverability
- Hit 5k followers before launching OF (gives some social proof when the link goes out)

**Don't rush this.** A brand-new IG dropping OF links from day 1 gets flagged. 4-6 weeks of organic-looking growth, THEN we wire up Bella for active conversion.

### Stage 4: OF launch (week 6+)

- Create OF account at $9.99/mo + custom content tiers
- Wire up Maya (V2 chatter) for on-platform chats — once V2 ships
- Bella's IG-to-OF funnel activates: keyword triggers, story-react triggers, comment triggers
- Initial promo: 50% off first month for early subs
- Monitor first 30 days closely, iterate prompts and content

### Stage 5: Scale + ops (ongoing)

- Daily content generation (n8n cron)
- Weekly batch of new visual assets
- Monthly retention review (which subs are still active at 30/60/90 days)
- A/B test sub price, promo cadence, content cadence
- Once one persona is at $10k+/mo, start persona #2

---

## The tech stack (what we build in this repo)

```
ofm-ig-dm-agent/
├── personas/                       # NEW: per-AI-creator persona definitions
│   └── mia/
│       ├── identity.md             # name, age, niche, voice
│       ├── visual_brief.md         # anchor images, style refs
│       ├── content_pillars.md
│       └── deployment.yml          # IG handle, OF handle, sub price, ManyChat IDs
├── content_engine/                 # NEW: image/video generation pipeline
│   ├── generate_image.py           # Flux + LoRA, batch generation
│   ├── generate_video.py           # Sora/Veo/Kling wrapper
│   ├── prompt_packs/               # per-persona prompt libraries
│   └── output/                     # gitignored generated assets
├── ig_engine/                      # NEW: IG content scheduling + posting
│   ├── post_scheduler.py           # cron-driven n8n trigger
│   ├── caption_writer.py           # Sonnet generates IG captions in persona voice
│   └── story_generator.py
├── of_engine/                      # NEW: OF content + Maya integration
│   ├── ppv_planner.py              # what PPV to send when
│   └── (V2 work, gated on lawyer review)
├── deliverables/                   # existing
└── simulator/                      # existing
```

This sits alongside what we already have. The Bella agent doesn't change — same persona, same flow, just different `creator_knowledge_base` doc per AI persona.

---

## Critical risks (and what we do about them)

### Risk 1: Platform policy

- **IG:** Meta requires AI-generated content disclosure on some content. Workaround: disclose where required, lean into it ("I'm an AI creator" is becoming a niche / kink in itself).
- **OF:** Increasingly accepts AI creators with disclosure. The biggest no-go is deepfake of real people. We build from synthetic bases only.
- **Mitigation:** Talk to a lawyer before OF launch. ~$500 consultation. Standard.

### Risk 2: Content quality bar

- AI-generated content quality has to be high enough that fans don't bounce.
- **Mitigation:** Heavy front-loaded investment in the LoRA training + visual pipeline. Don't skimp. A bad photoset kills the persona.

### Risk 3: Payment processor risk

- OF accounts can get flagged for "AI creator" if they get reported, payment processors can freeze.
- **Mitigation:** Diversify (1-2 personas first, learn the rules, then scale). Don't bet $50k of payment-processor liability on persona #1.

### Risk 4: "Catfish" framing

- Fans who feel deceived can leave bad reviews, report, get refunds.
- **Mitigation:** AI creator as a niche/aesthetic, not a deception. Lean into the persona ("hi, I'm Mia, I'm a digital creation, and I'm here to make your day better"). Real subset of the market specifically wants AI companions.

### Risk 5: This is creepy

- For some founders this is a non-starter.
- **EZJ's call:** he's in. The market exists, the legal path is clear with disclosure, the unit economics are real. Phase 2 we build.

---

## Sequencing (the parallel timeline)

| Month | Prong 1 | Prong 2 |
|---|---|---|
| Month 1 (June) | Harvey pilot launches | Mia persona definition + visual asset generation begins |
| Month 2 (July) | Outreach to 50 OFMs, 2-3 closes | Mia IG account live, organic growth phase |
| Month 3 (August) | $5-9k MRR from Prong 1 | Mia hits 5k IG followers, OF launches |
| Month 4 (Sept) | Prong 1 stable at $9-12k MRR | Mia at $5-15k/mo OF revenue |
| Month 5 (Oct) | Maintenance | Persona #2 starts, Mia hits $20-30k/mo |
| Month 6 (Nov) | — | Prong 2 revenue exceeds Prong 1 |
| Month 7+ | Wind down (or keep as ops cash flow) | Persona #3, 4, 5. Real company. |

---

## What we DON'T do in Phase 2

- **Deepfake of real people.** Synthetic personas only.
- **Underage content.** Hard line, always.
- **Hidden AI.** If the platform requires disclosure, we disclose.
- **Mass spam scaling.** 1 persona at a time until each is at $10k+/mo. Don't burn the pipeline by launching 20 personas at once.
- **Outsourced content.** We own the pipeline. No "buy 1000 AI photos from Fiverr." Quality control on us.

---

## What we need to decide before starting Phase 2 build

| Decision | Default | Action |
|---|---|---|
| Persona name and aesthetic | Mia, girl-next-door / fitness / alt | Joe + EZJ confirm or pick differently |
| Image gen platform | Flux 1.1 Pro via fal.ai | Pick one, lock pricing |
| Video gen platform | Veo 3 or Sora 2 | Pick one when we get to video |
| LoRA training (custom face) | YES (essential for consistency) | EZJ trains the first one |
| Legal review timing | Before OF launch (month 3-ish) | EZJ books a lawyer call |
| Phase 2 start date | This week (in parallel with Prong 1) | Confirmed |

---

## Next session work items (Prong 2)

1. EZJ + Joe lock Mia's full persona spec in `personas/mia/identity.md`
2. EZJ picks image-gen platform, runs first batch of 20 anchor images
3. EZJ creates `@mia.everyday` IG (or whatever handle is available) and FB Page
4. Joe starts iterating Mia's voice samples in `simulator/mia_test_creator.md` (already started)
5. Claudia (me) scaffolds `personas/`, `content_engine/`, `ig_engine/` directories
6. We get the first batch of generated content into the repo (gitignored, output only)
