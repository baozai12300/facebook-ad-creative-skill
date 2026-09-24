# Evidence Lock / Claim Safety

Evidence Lock protects factual integrity without suppressing creative expression. Classify every copy element into one of three tiers.

## Copy Tiers

### 1. Hard Claim

Requires matching user-supplied or verified evidence. This includes waterproofing, anti-theft, drop protection, exact capacity or material, RPM, wattage, measured duration, certification, ranking, bestseller status, numeric performance, percentage improvement, compatibility, proof, offer, and performance comparison.

When evidence is absent, remove the claim or replace it with a soft benefit or creative/lifestyle line. Never weaken the wording and pretend the same factual claim became safe.

### 2. Soft Benefit

May be reasonably derived from product category, visible structure, possible use scenes, selected audience, and lifestyle context, provided it does not state a measurable function or guaranteed outcome. Examples include `Ready for Everyday Moves`, `Made for City Life`, `Keep Essentials Close`, `From Commute to Weekend`, `Stay Ready On the Go`, and `Built Around Your Routine`.

Soft benefits are not added to `claims_used`. They must remain plausible, non-technical, non-medical, non-comparative, and free of guaranteed outcomes.

### 3. Creative / Lifestyle Copy

Expressive concept language such as `MOVE LIGHT`, `CITY MODE`, `ON THE GO`, `DAILY ESSENTIAL`, `MOVE WITH STYLE`, or `READY WHEN YOU ARE` does not require claim evidence because it is not presented as a product fact. It may be bold, editorial, and category-aware.

The Quality Gate must still reject creative wording that crosses into a hard claim. Capitalization or poster styling never exempts factual language from Evidence Lock.

## Sources

- `verified_facts`, `key_features`, `benefits`, `supplied_specs`, `offer_info`, `social_proof`, `verified_result_claims`, and `before_after_evidence` may support matching copy.
- `reference_image_visual_facts` may describe only plainly visible properties such as finish, form, display, grille, color, or silhouette.
- `inferred_context` may guide scene and styling only. It is never claim evidence.

Do not expand a supplied fact into a stronger claim. For example, `fast drying` does not authorize `3× faster`, a drying-time number, lower heat damage, or suitability for all hair types.

## Hard Gates

- Offer requires `offer_info`.
- Social proof, rating, testimonial, or review framing requires `social_proof`.
- Numeric specifications require a matching `supplied_specs` or `verified_facts` entry.
- Before/after or transformation requires `before_after_evidence` or `verified_result_claims`.
- Performance comparison requires supplied features, benefits, specs, verified facts, or verified result claims.

## Visual-Only Mode

When the input contains only product identity/category/reference imagery and no claim evidence, use `claim_mode: visual_only`. Favor product hero, editorial poster, detail crop, asymmetric grid, UGC real use, product handling, travel/everyday carry, gift presentation, and contextual product use. Generate differentiated soft-benefit and creative/lifestyle copy, but never manufacture a feature, specification, proof, or outcome.
