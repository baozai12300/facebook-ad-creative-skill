---
name: facebook-ad-creative-skill
description: Generate structured Meta/Facebook ecommerce ad creatives using product understanding, audience hypotheses, creative angles, placement-aware composition, visual style selection, concise model-ready prompts, and a mandatory quality gate.
---

# Facebook / Meta Ad Creative Skill v2

Use this skill for Facebook / Instagram / Meta ecommerce ad preview planning, ASC creative testing, product-led concepts, UGC-style static concepts, and placement-aware render-prompt compilation. The application chooses vision and image-generation providers.

## Orchestration Boundary

Read `references/engines/orchestration-pipeline.md` when integrating the Skill into an application.

- Application input: 1–8 product images and user product information.
- Application responsibility: call any configured vision-capable model, normalize its result through a Vision Adapter, manage preview UI and approval state, and call the selected image provider.
- Skill input: normalized `ProductAnalysis`, campaign settings, target market, and user-supplied product facts.
- Skill output: `CreativePreviewPlan[]` in `draft` status.
- The Skill does not know which vision provider produced ProductAnalysis and does not call an image-generation model.
- Compile image-provider payloads only after explicit user selection/approval.

## Core Principle

Do not send the image model a long strategy memo.

Separate the workflow into two layers:

1. **Creative planning layer** — audience, objective, angle, scene, visual style, layout, copy strategy, placement constraints.
2. **Render prompt layer** — a short visual instruction containing only what the image model needs to draw correctly.

The final render prompt should normally stay under ~220 words unless the product is unusually complex.

## Goal

Generate ads that are visibly different in concept, not merely different backgrounds. Each creative should communicate one clear buyer hypothesis in one glance while keeping the product recognizable, large enough for mobile viewing, and visually native to the selected Meta placement.

Do not claim guaranteed performance, approval, CTR, ROAS, or conversion lift.

## Mandatory Workflow

### Step 0 — ProductAnalysis Input

Receive normalized `ProductAnalysis` conforming to `references/templates/product-analysis.schema.json`. Do not bind this stage to a named model or provider. The application may use any multimodal model and provider-specific adapter.

Use visual identity and protected identity for fidelity; user-supplied facts for Evidence Lock; possible scenes and inferred context for creative context only. Unknowns and conflicts never become claims.

### Step 1 — Product Truth

Extract and lock:

- product identity and reference-image fidelity
- category and use case
- verified features
- buyer benefits
- price / offer only when supplied
- brand name / logo only when supplied
- banned or protected elements

Never invent product functions, ratings, discounts, reviews, certifications, ingredients, prices, or claims.

Read `references/engines/evidence-lock.md`. Build copy only from supplied or verified evidence. Visual observations may describe visible form only; inferred context may guide scene and styling but never become a product claim. When no claim evidence exists, use visual-only mode and neutral copy.

### Step 2 — Campaign Intent

Determine:

- objective: purchase / lead / awareness / retargeting / launch / offer
- awareness stage: cold / warm / hot
- placement: Feed / Story / Reels / Carousel cover / Advantage+ multi-placement
- aspect ratio
- text overlay mode

If unspecified, default to purchase + cold audience + Feed 4:5.

Read `references/engines/meta-placement-engine.md`.

### Step 3 — Audience Hypothesis

Read `references/engines/audience-engine.md` and `references/engines/audience-scene-fusion.md`.

Audience must change the visual evidence, not just appear as metadata. Translate the hypothesis into:

- use moment
- visible behavior
- environment cues
- relevant props
- camera distance
- copy tone

Choose the audience from the selected angle, category, core benefit, and awareness stage. Do not assign audience or scene by batch index.

Avoid sensitive-trait inference and stereotypes.

### Step 4 — Creative Angle

Read `references/engines/angle-engine.md`.

Select an angle because it fits the product + objective + awareness stage. Do not simply cycle angles in list order.

When compiling a batch, rank eligible angles using product/category, campaign goal, awareness stage, supplied benefits, price positioning, and supplied offer/proof evidence. `variation_strength` controls how broadly to sample the ranked pool. Offer and proof angles remain ineligible without user-supplied evidence.

Preferred Meta ecommerce angle families:

- Problem → Solution
- Benefit / Outcome
- Product Demonstration
- Feature → Benefit
- UGC / Testimonial framing
- Social proof only with real supplied proof
- Comparison / Old way vs New way
- Offer / Bundle / Value
- Lifestyle / Identity
- Objection handling
- Premium product hero
- Before / After only when truthful and compliant

Each creative gets one dominant angle. Secondary ideas must not compete with it.

### Step 5 — Scene + Visual DNA

Read `references/engines/scene-style-engine.md`.

Choose scene and style from product use, audience moment, price positioning, and angle. Avoid vague instructions such as only saying “high-conversion Facebook ad style”. Translate style into visible attributes:

- lighting
- material / texture treatment
- background character
- camera language
- color mood
- realism level
- graphic treatment

### Step 6 — Composition / Layout

Read `references/engines/layout-engine.md`.

Select one layout pattern and define geometry before writing the prompt:

- product position and approximate canvas share
- headline zone
- proof / callout zone if used
- visual flow
- negative space
- safe margins
- CTA treatment, if any

The layout must fit the selected angle. Do not use the same scene-style-layout combination twice in one batch.

### Step 7 — Copy Strategy

Copy is subordinate to the visual concept.

Classify copy before rendering:

1. **Hard claim** — specifications, measurable performance, certifications, protection, exact materials/capacity, comparison, proof, or offer; requires matching evidence.
2. **Soft benefit** — plausible category-, scene-, audience-, or routine-based language without measurable or guaranteed product facts.
3. **Creative / lifestyle copy** — expressive editorial language that is not a product fact and does not require evidence.

Evidence Lock applies strictly to hard claims. It must not force soft benefits and creative/lifestyle copy into generic neutral wording.

Lifestyle and UGC headlines must be derived from the product category, selected benefit, angle, and use scene. Do not reuse one generic lifestyle headline across unrelated products or across most of a batch.

For static Meta creatives:

- no-text mode: absolutely no rendered words, pseudo-text, badges, buttons, labels, or fake UI
- light mode: headline only, optionally one short support line
- standard mode: headline + up to 2 compact benefit callouts
- heavy mode: use only for infographic / offer / comparison layouts

Do not force CTA buttons into every image. Meta's system CTA exists outside the image.

Treat “20% text” only as a visual-density guideline, not a Meta policy rule.

Use layout-driven typography where appropriate: oversized headlines, small captions, vertical micro-text, split hierarchy, numbered non-claim labels, detail captions, and poster-style composition. Functional callouts still require evidence.

When exact text rendering is unreliable for the chosen model, prefer a text-light visual or generate the visual first and add typography in the product editor.

### Step 8 — Render Prompt Compilation

Read `references/engines/prompt-compiler.md`.

The render prompt must contain only:

1. output format and ratio
2. immutable product identity instruction
3. scene and action
4. composition geometry
5. lighting / camera / style
6. exact on-image copy, only when required
7. negative constraints

Do not dump audience-analysis prose, campaign theory, rationale, interest lists, difference statements, or internal scoring into the image prompt.

### Step 9 — Batch Diversity

Read `references/engines/variation-strategy.md`.

For 4 variants, change at least three major dimensions per creative and ensure the batch includes:

- one direct product-clarity creative
- one real-use/lifestyle or UGC creative
- one benefit/problem creative
- one structurally different concept such as proof, comparison, offer, premium hero, or objection handling

For 8 variants, diversify angles first, then layouts, scenes, camera language, and visual style. Do not create eight cosmetic variations of one template.

### Step 10 — Mandatory Quality Gate

Read `references/engines/quality-gate.md`.

Reject and revise any creative that fails product fidelity, one-glance clarity, product prominence, placement safety, typography legibility, claim accuracy, or batch diversity.

### Preview + Approval Boundary

Return the approved-quality concepts as `CreativePreviewPlan[]`, but keep their initial status `draft`. The frontend may let the user select, edit, regenerate, or delete plans. Only the user's selected plans become `approved`; only approved plans may be converted into provider-neutral render payloads. Do not generate images during preview compilation.

## Product Fidelity — MUST

When a reference product image exists:

- preserve silhouette, proportions, colorway, material, packaging, logo placement, hardware, controls, labels, and distinctive details
- do not redesign the SKU
- do not add accessories or variants that were not provided
- scene and lighting may change; product identity may not

For multi-image batches, describe the product identity consistently across every prompt.

## Application-Owned Model Routing Guidance

These are examples for the application router, not Skill dependencies.

### GPT Image 2

Prefer when:

- readable on-image text is important
- exact layout / typography matters
- product realism and commercial polish are priorities

### Nano Banana / Gemini image models

Prefer when:

- visual ideation, scene transformation, or image-to-image adaptation matters more than dense typography
- use short copy or no copy when possible

Do not make the Skill dependent on one model name. The application may route to any capable image backend.

## Output Schema

For each creative, return a draft preview plan and a compact render prompt:

```json
{
  "creative_id": "C01",
  "title": "Problem → Solution",
  "status": "draft",
  "strategy": {
    "audience": "...",
    "angle": "Problem → Solution",
    "message": "..."
  },
  "visual": {
    "scene": "...",
    "product_action": "...",
    "layout": "...",
    "camera": "...",
    "lighting": "...",
    "visual_dna": "..."
  },
  "copy": { "headline": "...", "support": "" },
  "placement": { "platform": "Meta", "placement": "Feed", "ratio": "4:5" },
  "evidence": { "claims_used": [], "sources": [] },
  "render_prompt": "...",
  "quality": { "pass": true, "findings": [] }
}
```

## Read When Needed

- Audience rules: `references/engines/audience-engine.md`
- Audience-scene bridge: `references/engines/audience-scene-fusion.md`
- Angle rules: `references/engines/angle-engine.md`
- Scene and style: `references/engines/scene-style-engine.md`
- Layout / composition: `references/engines/layout-engine.md`
- Meta placement rules: `references/engines/meta-placement-engine.md`
- Render prompt compiler: `references/engines/prompt-compiler.md`
- Evidence lock and claim safety: `references/engines/evidence-lock.md`
- Provider-agnostic orchestration: `references/engines/orchestration-pipeline.md`
- Batch diversity: `references/engines/variation-strategy.md`
- Quality gate: `references/engines/quality-gate.md`
- Schemas: `references/templates/product-analysis.schema.json`, `references/templates/creative-preview-plan.schema.json`, `references/templates/render-payload.schema.json`

## Default Assumptions

- Platform: Meta
- Placement: Feed
- Ratio: 4:5
- Objective: purchase
- Awareness: cold
- Text: light
- Generation count: 4
- Variation strength: high
- Language: user-selected target market language; otherwise match user request

## Non-Negotiable Rules

- Product fidelity is more important than decorative creativity.
- One creative = one dominant message.
- The product should be understandable at mobile-feed size.
- Do not render fake Meta/Facebook UI, reaction bars, sponsored labels, comments, or platform logos.
- Do not invent proof, offers, claims, discounts, ratings, reviews, or guarantees.
- Do not use generic stock-ad language when a concrete use moment can communicate the idea visually.
- Do not put internal reasoning or strategy notes into the final image prompt.
- When a creative is weak, revise the concept or composition before adding more prompt adjectives.
