# Render Prompt Compiler

The compiler converts a finished creative plan into a short image-generation prompt. It must remove strategy prose that the image model does not need.

## Why This Exists

Image models perform worse when the prompt mixes:

- audience research
- campaign theory
- angle rationale
- interest lists
- internal scoring
- variation explanations
- long copywriting notes

Keep those in the planning object. The render prompt should describe the image to draw.

## Prompt Order

Use this order:

1. Output type + aspect ratio
2. Product identity / fidelity
3. Scene + action
4. Composition geometry
5. Lighting / camera / visual style
6. Exact text, only if needed
7. Negative constraints

## Compact Template

```text
Create a {aspect_ratio} Meta ecommerce ad image.

PRODUCT: Preserve the supplied product reference exactly: {identity_constraints}. Do not redesign the SKU.

SCENE: {scene_and_action}.

COMPOSITION: {product_position_and_scale}. {headline_zone}. {support_zone}. Keep {negative_space} uncluttered. Visual flow: {visual_flow}.

LOOK: {lighting}. {camera_language}. {visual_style}. {color_mood}. Commercial realism, believable materials, clean separation.

TEXT: {exact_copy_instruction}

AVOID: {negative_constraints}.
```

## Product Identity Block

When a reference image exists, include only concrete identity features that help preserve the SKU:

- silhouette
- proportions
- colorway
- material
- packaging shape
- logo position
- controls / hardware
- distinctive surface details

Do not describe unrelated strategy here.

## Text Modes

### none

Use:

`No rendered words, letters, badges, buttons, labels, logos added by the model, or pseudo-text. Preserve only native text already printed on the supplied product when applicable.`

### light

Usually headline only, optionally one short supporting line.

Use exact quoted text and specify one placement zone.

### standard

Headline plus up to two short benefit labels.

### heavy

Only for infographic, comparison, or offer layouts. Keep the prompt explicit and avoid many small text elements.

## Model-Specific Adaptation

### GPT Image 2

Can accept more explicit typography and geometry instructions. Still keep the prompt concise.

Recommended additions:

- exact quoted copy
- alignment
- approximate text zone
- natural line breaks
- high contrast
- no extra invented copy

### Nano Banana / Gemini image models

Favor visual instructions over dense typography.

If exact small text is important, prefer:

- headline-only rendering, or
- generate a clean visual and add typography in the editor afterward

Do not repeat the same paragraph three times using synonyms.

## Prompt Budget

Target 120–220 words for ordinary ecommerce creatives.

Use more only when the SKU has complex fidelity requirements.

## What Must Stay Out of the Render Prompt

Never include:

- “target audience is…” unless it changes visible casting/action
- interest keyword lists
- awareness-stage theory
- campaign objective explanation
- “this variation differs from…”
- scoring notes
- creative rationale
- instructions to follow another markdown file
- performance claims

Convert useful strategy into visible direction instead.

Example:

Bad:
`Target audience: busy professionals interested in productivity and commuting.`

Better:
`Morning commuter setting, product being used one-handed beside a laptop bag and takeaway coffee; tight mobile-feed framing.`

## Final Check

Before emit:

- Can the prompt be visualized without reading the planning JSON?
- Is the product identity explicit?
- Is there one dominant concept?
- Is the layout geometric rather than abstract?
- Is every requested word exact?
- Can any sentence be removed without losing visual information?

If yes to the last question, shorten it.
