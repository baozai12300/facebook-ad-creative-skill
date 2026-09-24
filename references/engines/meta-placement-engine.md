# Meta Placement Engine

This engine adapts a creative concept to Meta placements without turning placement rules into the creative idea itself.

## Supported Placement Profiles

### Feed — 4:5 preferred

Default canvas: 1080 × 1350.

Use when the user wants a general Meta/Facebook/Instagram static ad and does not specify placement.

Rules:

- Keep critical product, face, logo, and headline inside the center ~80% of the composition.
- Use a strong first-glance focal point.
- Product should usually occupy enough visual area to remain recognizable on a phone screen.
- Avoid placing important copy directly on extreme edges.
- Design for mobile first even when the ad may also appear on desktop.

### Square Feed — 1:1

Default canvas: 1080 × 1080.

Use for carousel consistency, catalog-like concepts, or user-requested square output.

Rules:

- Keep primary content centered.
- Avoid squeezing a 4:5 composition into square by naive cropping.
- Recompose product and copy rather than scaling everything down.

### Story — 9:16

Default canvas: 1080 × 1920.

Rules:

- Keep important content away from top and bottom UI regions.
- Use the middle visual field for headline, product, faces, and proof.
- Favor vertical product/action flow.
- Do not put the only key message at the bottom of the frame.

### Reels Static / Poster — 9:16

Default canvas: 1080 × 1920.

Rules:

- Treat the lower portion as high-risk for overlays and controls.
- Keep the product and primary message in the upper-middle safe region.
- If the image is intended as a Reel cover or static creative, make it readable in a quick vertical scroll.
- Avoid tiny multi-column information structures.

### Carousel

Use consistent ratio and visual system across cards.

Rules:

- Card 1: hook / outcome / product clarity.
- Middle cards: one message per card.
- Final card: resolution / offer / product hero / CTA direction when appropriate.
- Keep product identity, palette, typography, and brand cues consistent across the sequence.
- Do not create a carousel by slicing one large poster into multiple cards unless explicitly requested.

### Advantage+ Multi-Placement

When the user asks for broad Meta placement compatibility, do not generate one image and blindly crop it.

Create a master concept, then adapt its composition into separate ratio variants:

- Feed 4:5
- Square 1:1 when needed
- Story/Reels 9:16

The angle, product identity, offer, and visual DNA should remain consistent while geometry changes.

## Safe Composition Principles

- Platform UI belongs outside the generated image. Never draw Facebook / Instagram interface elements, reaction bars, sponsored labels, comments, profile headers, or fake native controls.
- Meta's external CTA button means an in-image CTA button is optional.
- Text density is a visual readability choice; do not treat the historical 20% rule as an approval rule.
- Important content should survive modest automated cropping.
- Recompose for each ratio rather than stretch or crop blindly.

## Placement Selection

If placement is unspecified:

1. Use Feed 4:5 as the default static-ad composition.
2. If the user requests multiple ratios, derive separate composition plans from the same concept.
3. If the creative depends on a tall environment or human action, consider 9:16 adaptation in addition to Feed.

## Output Fields

For each creative expose:

```json
{
  "placement": "feed",
  "aspect_ratio": "4:5",
  "canvas": "1080x1350",
  "safe_composition": "center 80%",
  "adaptation_notes": "..."
}
```
