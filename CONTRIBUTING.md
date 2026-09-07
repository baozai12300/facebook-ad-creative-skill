# Contributing

Contributions are welcome.

Good contribution areas:

- new product category presets
- additional audience, angle, scene, style, and layout rules
- localized prompt examples
- image model adapters
- prompt lint checks
- example outputs from real product briefs

## Guidelines

- Keep `SKILL.md` concise.
- Put detailed rules in `references/`.
- Do not add fake reviews, fake endorsements, or guaranteed performance claims.
- Avoid templates that imply sensitive personal attributes.
- For health, finance, supplements, and similar categories, keep claims conservative.
- Add or update examples when changing prompt behavior.

## Validation

Run:

```bash
python -m pytest tests/test_compile_creatives.py
python scripts/compile_creatives.py examples/beauty-serum.json
```
