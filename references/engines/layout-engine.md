# Layout / Composition Engine

The layout engine converts the selected creative angle into explicit image geometry. Do not use abstract layout names without placement instructions.

## Core Principle

One layout should make the dominant message obvious in under one second on a mobile feed.

Layouts should create an art-directed advertising system, not merely place a product over a background. Depending on angle and placement, use editorial typography, multi-level hierarchy, oversized or vertical type, detail crops, asymmetric grids, graphic shapes, thin rules, texture blocks, poster composition, split regions, and numbered non-claim labels such as `01` / `02`.

Decorative numbers are structural labels only. Any number that communicates capacity, performance, quantity, rating, price, duration, or specification remains a hard claim and requires evidence.

Every layout definition must specify:

- `product_anchor`: where the product sits
- `product_scale`: approximate percentage of canvas height/area
- `headline_zone`: where text may appear
- `support_zone`: optional proof/callout area
- `negative_space`: where the image must stay quiet
- `visual_flow`: first → second → third focal point
- `safe_margin`: minimum edge clearance
- `typography`: scale, direction, and hierarchy
- `graphic_structure`: grid, crop, rules, shapes, blocks, or callout system

## Layout Signature Contract

A layout label is not enough. Every selected layout must compile a `structural_signature`, `composition_geometry`, structured `typography_structure`, and structured `graphic_structure` into the final render prompt.

The signature must state concrete geometry: number and relative size of zones, product scale and anchor, crop behavior, dedicated text zones, negative space, and the secondary visual element. The quality gate must fail when the generated prompt describes a generic centered poster while claiming a structurally different layout.

Required signatures include:

- `hero_product_first`: one dominant complete product at 45–70%, one headline field, no collage
- `grid_multi_panel`: at least three unequal zones—dominant full view, secondary detail crop, separate type panel
- `editorial_type_led`: oversized headline, micro-label, caption, deliberate line breaks, product/type interaction
- `detail_macro_plus_full`: visible-detail macro at 35–60% plus a separate complete product view
- `human_native_use`: candid phone-shot use, environmental context, no editorial system
- `minimal_art_directed`: off-center product, restrained type, 55–70% deliberate empty space
- `polished_human_lifestyle`: action and environment lead while product remains 35–45% prominent

`typography_structure` must explicitly contain headline, scale, position, alignment, support, micro-label, orientation, line breaks, and product/type interaction. Graphic elements may include panels, crop windows, grids, thin rules, texture blocks, shapes, and non-claim number labels. Never use fake badges, ratings, certifications, offers, or interface chrome.

## Layout Patterns

### L1 — Product Hero
Best for: premium hero, feature clarity, retargeting.

- Product centered or slightly offset, 48–68% of canvas height
- Clean background with strong tonal separation
- Headline in upper-left or upper-center safe zone
- Optional one support line below headline
- No decorative cards unless they serve the message

### L2 — Benefit Focus
Best for: feature → benefit, problem solution.

- Product occupies 45–60% of canvas
- 1–2 short callouts placed around product without touching silhouette
- Clear whitespace between callouts and product
- Main headline above or beside product
- Avoid more than 2 callout clusters on mobile

### L3 — Problem → Solution Split
Best for: pain solution, old way vs new way.

- Two visual regions with strong contrast
- Problem side visually simpler and less desirable
- Solution/product side brighter and product-dominant
- Product must not be split across the divider
- Copy limited to one short phrase per side when used

### L4 — Lifestyle Story
Best for: emotional benefit, identity, use moment.

- Product used naturally in a believable environment
- Product remains clearly identifiable, ideally 30–45% of frame prominence
- Person/action can lead, but product cannot disappear
- Headline uses available negative space rather than covering face/product

### L5 — UGC Native Static
Best for: trust, cold audience, testimonial-style framing.

- Phone-shot realism, imperfect-but-believable framing
- Product in hand / on counter / in use
- Minimal overlay: usually headline only
- Avoid polished studio symmetry
- Never fake comments, likes, sponsored labels, or Meta UI

### L6 — Review / Proof Card
Best for: real supplied review, verified proof.

- Product remains the primary object
- Proof card is secondary, 18–28% of canvas
- Quote must be short and supplied by user
- Avoid fabricated avatars, ratings, or review counts

### L7 — Offer / Value
Best for: provided discount, bundle, launch, hot audience.

- Product large and central
- Offer chip or price zone is visually strong but smaller than product
- Headline states value clearly
- CTA button inside the image is optional, not mandatory
- Never invent urgency or discount data

### L8 — Comparison
Best for: competitor-free comparison, old/new workflow, feature contrast.

- Use two clear columns or top/bottom comparison
- Prefer visual attributes over dense tables
- Product on the preferred side should be dominant
- Do not name competitors unless user supplied and comparison is accurate

### L9 — Minimal Editorial
Best for: premium positioning, design-led products.

- 55–75% negative space
- Product 35–55% canvas prominence
- Controlled shadow, texture, and material detail
- Very little or no on-image copy

### L10 — Infographic Lite
Best for: technical or feature-heavy products.

- Product central, 40–55% canvas
- Maximum 2–3 concise benefit labels
- Use lines/arrows sparingly
- Labels must describe supplied facts only
- Avoid dense specification sheets

### L11 — Editorial Poster

- Oversized headline and strong scale contrast
- Product can overlap decorative typography without losing silhouette clarity
- Use asymmetric crops, thin rules, shape fields, and one small caption
- Keep all wording soft-benefit, creative/lifestyle, or evidence-backed

### L12 — Detail Crop

- Pair one close material/detail crop with one complete product view
- Use a vertical micro-label or numbered non-claim marker
- Detail captions may describe visible form only; functional captions require evidence

### L13 — Asymmetric Grid

- Use uneven grid cells, one deliberate empty cell, and a strong off-center anchor
- Combine an oversized headline with one small caption
- Texture blocks and graphic shapes must support hierarchy rather than decorate randomly

## Layout Selection Rules

Choose layout from the angle, not randomly:

- Product clarity / premium → L1 or L9
- Feature benefit → L2 or L10
- Problem solution → L3
- Lifestyle / identity → L4
- UGC / trust → L5
- Social proof → L6
- Offer / bundle → L7
- Comparison / objection → L8
- Editorial/lifestyle identity → L11 or L13
- Product form/detail demonstration → L12

If the selected layout fights the angle, change the layout before writing the prompt.

## Batch Diversity

In a four-image batch, use at least three structurally different layout families.

In a high-variation five-image batch, require at least four distinct structural signatures and reject duplicate structural fingerprints. Prefer five distinct signatures when five layouts are available.

In an eight-image batch, do not repeat the same layout more than twice unless the user explicitly requests controlled A/B variants.

## Text Rules

- Headline should normally occupy one visual zone only
- Keep text away from product silhouette and faces
- Use natural line breaks
- Avoid tiny captions
- A CTA inside the image is optional
- Treat text density as a readability decision, not a platform-policy quota
