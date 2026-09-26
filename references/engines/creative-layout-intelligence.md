# Creative Layout Intelligence

Creative Layout Intelligence is optional external design knowledge produced by the application's Creative Layout Miner. The application calls `GET /api/creative/recommend`; this Skill never performs the HTTP request and never depends on a particular Miner implementation.

## Input Boundary

Consume only normalized `creative_layout_intelligence`: match metadata, grammar arrays for layout/composition/product geometry/typography/graphics/style, and at most three reference fingerprints. References are structural inspiration only. Never request an exact recreation, expose a reference URL in the render prompt, or copy one ad's complete design.

## Strength

- `strong`: exact industry + ad type + ratio with at least 20 samples
- `medium`: exact match with at least 8 samples, or a two-dimension match with at least 20
- `soft`: usable recommendation with any positive sample count
- `none`: disabled, malformed, empty, unavailable, timed out, or zero samples

Strong intelligence drives at least 70% of a batch; medium at least 50%; soft may influence one concept. Preserve at least four structural signatures in a high-variation five-concept batch.

## Fusion

Apply intelligence before final layout selection:

`Campaign Intent → Creative Layout Intelligence → Layout Candidate Pool → Angle/Scene adaptation → Final Layout Selection → Typography → Prompt Compiler`

Build 6–10 candidates by combining recommended layout families, composition types, headline positions, product geometry, typography levels, and graphic hints. Select concepts from this pool before adapting the ranked angle and scene. Do not pre-allocate Hero, Lifestyle, or Detail quotas.

At strong strength, at least 70% of final plans come from the candidate pool. At medium strength, at least 50%. Soft strength may leave the native engine dominant.

Map Miner layout names into the existing layout taxonomy. Normalize product position and scale into concrete geometry; headline position, typography levels, and density into the existing typography structure; and known graphic hints into explicit panels, cutouts, headline blocks, strips, micro-labels, rules, or grids. An offer badge is permitted only with supplied offer evidence.

Normalize visual style strings into the existing Visual DNA taxonomy. Do not make arbitrary style text a hard instruction.

## Prompt and Quality

Compile selected knowledge into concise design language. Never dump Miner JSON, sample metadata, reference records, or technical source fields into the render prompt.

When a plan declares `layout_intelligence.used: true`, expose its selected layout family, composition type, and reference pattern. `intelligence_applied_correctly` checks partial agreement across layout family, composition, product geometry, typography, and graphic structure. Strong and medium plans must match at least two applicable dimensions. Soft intelligence never causes a strict quality failure.

If intelligence is absent or unusable, behavior must remain on the native Creative Engine path.
