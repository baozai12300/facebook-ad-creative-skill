# Creative Quality Gate

Every creative must pass this gate before delivery. If any MUST item fails, revise the concept or prompt rather than merely adding more adjectives.

## MUST Checks

### 1. Product Fidelity

Pass only if:

- reference product identity is preserved
- silhouette, colorway, material, packaging, controls, and distinctive details are not redesigned
- no unprovided accessories or variants are introduced

### 2. One-Glance Message

Pass only if a viewer can identify the dominant message in roughly one second at mobile size.

Fail when:

- several angles compete
- headline, proof, feature labels, CTA, and decorative elements all demand equal attention
- the concept needs a paragraph of explanation to make sense

### 3. Product Prominence

Pass only if the product is easy to identify in the selected placement.

Fail when:

- environment overwhelms the SKU
- product is tiny
- a person's face or decorative prop becomes the true focal point without a strategic reason

### 4. Layout Clarity

Pass only if:

- focal hierarchy is explicit
- product and text zones do not collide
- negative space exists
- visual flow is intentional
- important elements respect placement-safe composition

### 5. Copy Accuracy

Pass only if:

- supplied copy is preserved exactly when exact rendering is requested
- no invented price, discount, rating, review, certification, guarantee, or claim appears
- copy density fits the selected layout

### 6. Typography Legibility

For text-enabled creatives:

- headline readable at phone-feed size
- strong contrast
- natural line breaks
- no pseudo-text or duplicated text
- no tiny multi-line paragraph overlays

If the model is poorly suited to exact typography, reduce copy or route typography to a post-generation editor.

### 7. Placement Fit

Pass only if:

- ratio matches the requested placement
- critical content is inside safe composition zones
- 9:16 concepts keep key information away from high-risk top/bottom UI areas
- one master creative is not naively cropped across every ratio

### 8. Realism / Commercial Finish

Pass only if:

- materials and product proportions are believable
- hands/faces/anatomy are acceptable when present
- background props support the use case
- image does not have obvious accidental AI artifacts

### 9. Claim / Proof Integrity

Pass only if:

- social proof comes from user-supplied proof or is explicitly excluded
- before/after is truthful and appropriate
- regulated-category claims stay within provided facts and compliance notes

### 10. Batch Diversity

For a batch, pass only if variants differ at the hypothesis level.

Check differences across:

- dominant angle
- use moment
- scene
- layout family
- camera language
- style / visual DNA
- text strategy

A background-color swap does not count as a new creative hypothesis.

## Batch-Level Minimums

### 4 creatives

Require:

- 4 distinct dominant angles where practical
- at least 3 different layout families
- at least 1 product-clarity creative
- at least 1 lifestyle or UGC/use-moment creative
- at least 1 problem/benefit creative

### 8 creatives

Require broader distribution across:

- cold-audience hooks
- product clarity
- proof/trust when available
- lifestyle/use moments
- offer/value when provided
- objection/comparison or premium positioning when appropriate

Do not force an angle that does not fit the product merely to fill a quota.

## Scoring Output

Use a simple pass/fail object, not a fake performance score:

```json
{
  "pass": true,
  "findings": [],
  "revised": false
}
```

If failed:

```json
{
  "pass": false,
  "findings": ["product too small", "headline overlaps product"],
  "revision_action": "switch to Product Hero layout and reduce copy to headline only"
}
```

## Revision Priority

Fix in this order:

1. product fidelity
2. concept / angle clarity
3. layout geometry
4. product scale
5. copy density
6. style polish

Do not try to solve a bad concept with extra stylistic adjectives.
