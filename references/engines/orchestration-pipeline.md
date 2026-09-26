# Model-Agnostic Creative Orchestration

The application owns model selection and API calls. The Facebook Ad Creative Skill owns strategy and preview-plan compilation only.

## Pipeline

```text
Product images (1–8)
→ configured vision-capable provider
→ Vision Adapter
→ normalized ProductAnalysis
→ Evidence Lock + Creative Engine
→ CreativePreviewPlan[] (draft)
→ frontend selection / edit / regenerate / delete
→ approved plans
→ provider-neutral render payloads
→ configured image-generation provider
→ final ad images
```

## Boundaries

- `analyze_product(images, model, provider, user_product_info)` is an application-layer dependency-injection boundary. Any provider is valid if it accepts image input and returns data that its adapter can normalize.
- The Vision Adapter converts provider-specific keys into `references/templates/product-analysis.schema.json`. Provider names and response shapes never enter Creative Engine decisions.
- The Skill accepts normalized ProductAnalysis plus campaign settings and user facts. It returns `CreativePreviewPlan[]`; it does not generate images.
- Preview plans remain `draft` until the user selects them. Edits are applied before approval. Only `approved` plans may become render payloads.
- `build_render_payloads(...)` prepares requests but performs no external call.
- `generate_ad_image(...)` is an optional application boundary called only after approval; the selected provider implements the actual request.
- The application owns Creative Layout Miner HTTP calls and passes normalized results as optional `creative_layout_intelligence`. Miner failure must never block creative planning.

## Evidence mapping

- `ProductAnalysis.user_supplied_facts` enters verified claim evidence.
- `ProductAnalysis.visible_facts` may describe literal visible identity and fidelity, but is not promoted into performance copy.
- `ProductAnalysis.inferred_context` and `possible_use_scenes` may guide scene selection only.
- `unknowns` and `conflicts` never enter claims.
- `protected_identity` compiles into the product-fidelity portion of each render prompt.

## Frontend state

Recommended actions are `Select`, `Edit`, `Regenerate this plan`, `Delete`, and `Generate selected`. Regeneration returns a new draft plan; it must not silently trigger image generation. The frontend or application service stores approval state and passes only approved plans to the image-provider layer.

## Interfaces

The reference implementation is `scripts/orchestrate_creatives.py`:

- `VisionAdapter.normalize(...) -> ProductAnalysis`
- `analyze_product(...) -> ProductAnalysis`
- `create_creative_preview_plans(...) -> CreativePreviewPlan[]`
- `approve_preview_plans(...) -> approved CreativePreviewPlan[]`
- `build_render_payloads(...) -> RenderPayload[]`
- `generate_ad_image(...)` delegates one approved payload to an injected provider

These interfaces are model-agnostic. GPT, Gemini, Claude, an OpenAI-compatible endpoint, or another multimodal/image provider is configuration, not Creative Skill logic.
