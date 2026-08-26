# Variation Strategy

Batch generation must create meaningfully different ad hypotheses.

## Controlled Dimensions

- audience segment
- interest cue
- pain point
- selling angle
- scene
- visual style
- composition
- main visual element
- copy tone
- color mood
- camera language
- layout

## Hard Rules

- In a 4-image batch, every image must differ in at least 3 dimensions.
- In an 8-image batch, no two adjacent images may use the same angle or visual style.
- Do not repeat the same scene-style-layout combination in a batch.
- Include at least one direct product clarity creative in every batch.
- Include at least one lifestyle or UGC creative in every batch of 4 or more.
- When `variation_strength` is `high`, rotate every major dimension before repeating any.

## Difference Statement

Every prompt must include a sentence such as:

`This variation focuses on [angle] for [audience], using a distinct [scene/style/layout] compared with the other creatives in this batch.`

