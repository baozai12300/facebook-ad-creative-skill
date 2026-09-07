# Audience-Scene Fusion Engine

Use this engine after forming an audience hypothesis and before choosing the final scene, style, camera language, and copy.

## Required bridge

For each creative, define:

- `use_moment`: the specific moment in which the product becomes relevant.
- `visible_behavior`: an observable action that demonstrates use, friction, desire, or payoff.
- `environment_cues`: 2-4 concrete setting details that make the moment believable.
- `prop_cues`: only relevant objects that support the use case without competing with the product.
- `casting_direction`: whether a person is needed and, if so, their role and action rather than sensitive identity attributes.
- `camera_language`: framing and viewpoint appropriate to how this audience discovers or evaluates the product.
- `copy_tone`: vocabulary and emotional register suited to the audience's awareness stage and buying motivation.
- `why_it_fits`: one sentence connecting audience, moment, product benefit, and creative angle.

## Construction sequence

1. Start from the audience's job-to-be-done, pain point, desire, and awareness stage.
2. Choose a real use moment, not a generic category backdrop.
3. Select behavior and environmental evidence that makes the benefit understandable without reading the caption.
4. Decide whether showing a person improves clarity. Prefer a product-led scene when casting would be arbitrary.
5. Match the visual style, camera language, and copy tone to the same hypothesis.
6. Write the complete bridge into the image-model prompt.

## Batch rules

- Every variant must test a different audience-moment-angle hypothesis, not merely change the background.
- Do not reuse the same use moment or visible behavior in adjacent variants.
- At least one variant must communicate the audience through product context without relying on a person.
- When generating four or more variants, include both an immediate-use moment and an aspirational or identity-reinforcing moment when appropriate.
- Props, wardrobe, rooms, and locations must remain subordinate to a clear, large product hero.

## Safety and realism

- Do not infer or depict protected or sensitive traits unless the user explicitly provides a legitimate requirement and the request is safe.
- Avoid stereotypes, caricatures, token casting, status clichés, and implausible lifestyle signals.
- Do not imply personal knowledge about the viewer. Describe a buyer hypothesis, not “people like you.”
- Do not invent product capabilities, professional endorsements, outcomes, prices, ratings, or social proof.
