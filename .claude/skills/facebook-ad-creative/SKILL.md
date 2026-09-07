---
name: facebook-ad-creative
description: Generate structured Facebook/Meta ad image creative plans and model-ready prompts for ecommerce and consumer products, with audience, angle, scene, style, layout, text overlay, and batch variation strategy.
---

# Facebook Ad Creative Skill

Use this skill when the user wants Facebook / Meta ad image creatives, ecommerce ad visuals, ASC-friendly creative testing ideas, product image ad prompts, batch ad variants, or prompts for GPT Image 2 / Nano Banana.

## Goal

Create structured ad creative plans and image model prompts that help users explore multiple distinct creative directions for the same product. Do not claim guaranteed ad performance. Frame the output as structured creative exploration for Meta's delivery and testing systems.

## Workflow

1. Parse the product brief.
2. Normalize missing fields with practical defaults.
3. Build audience hypotheses.
4. Select creative angles.
5. Select scenes and styles.
6. Select layouts and text overlay mode.
7. Generate batch variants with clear differences.
8. Produce Creative Plan and Model Prompt for each creative.
9. Include GPT Image 2 and Nano Banana prompt adaptations.
10. Run a basic quality check for diversity, mobile readability, product focus, and text density.

## Read When Needed

- Input and output schemas: `references/templates/input.schema.json`, `references/templates/creative-output.schema.json`
- Prompt templates: `references/templates/prompt-templates.json`
- Audience rules: `references/engines/audience-engine.md`
- Angle rules: `references/engines/angle-engine.md`
- Scene and style rules: `references/engines/scene-style-engine.md`
- Layout rules: `references/engines/layout-engine.md`
- Batch diversity rules: `references/engines/variation-strategy.md`

## Default Assumptions

- Platform: Facebook / Meta
- Placement: feed first, with mobile-first composition
- Aspect ratio: 4:5 unless user specifies story/reels, then 9:16
- Language: match user language, unless the product market implies English
- Text overlay: light text by default
- Generation count: 4 by default
- Variation strength: high for batch testing

## Output Format

Return concise Markdown plus structured JSON when useful:

```json
{
  "creative_plans": [],
  "model_prompts": [],
  "quality_checks": []
}
```

Each creative must include:

- target audience
- interest cues
- pain point or desire
- selling angle
- scene
- visual style
- layout
- headline/subheadline/bullets/CTA when applicable
- difference from other variants
- negative constraints
- GPT Image 2 prompt
- Nano Banana prompt

## Important Rules

- Make each batch variant meaningfully different.
- Do not use the same scene, style, and layout combination twice in one batch.
- Keep product visible and large enough for mobile feed.
- Keep text overlay short and readable.
- Treat `text_overlay_mode` as authoritative. When it is `none`, prohibit all rendered words, letters, CTA buttons, badges, logos, and pseudo-text. Otherwise, on-image copy is required rather than optional.
- For text-enabled creatives, define an exact headline, optional subheadline, no more than 2-3 compact benefit callouts, and an optional CTA. Keep the total text footprint near or below 20% of the canvas.
- Put typography instructions inside every model prompt: exact copy, language, hierarchy, placement, alignment, contrast, safe margins, and natural line breaks. Never rely on a separate prose plan to make the image model render text.
- Require correct spelling. Prohibit garbled glyphs, placeholder pseudo-text, duplicated copy, and model-invented prices, discounts, ratings, brands, claims, or offers.
- Adapt density to the selected layout: UGC and lifestyle may use only a headline; benefit and callout layouts may use 2-3 short labels; never force every copy element into every layout.
- Avoid crowded compositions and generic stock-ad language.
- Use social proof only when provided or clearly framed as placeholder/example copy.
- For regulated categories such as health, finance, or supplements, avoid medical claims and add compliance cautions.
- Never promise platform performance, approval, or ROAS.

## Script Option

For deterministic prompt compilation from JSON input, run:

```bash
python .claude/skills/facebook-ad-creative/scripts/compile_creatives.py examples/beauty-serum.json
```
