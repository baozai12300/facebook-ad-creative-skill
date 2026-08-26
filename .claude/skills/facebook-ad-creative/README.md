# Facebook Ad Creative Skill

This folder is the loadable Skill package.

It turns product information into Meta/Facebook ad creative plans and image-generation prompts. The skill is optimized for ecommerce and consumer product ad testing where multiple image variants must be meaningfully different.

## Files

- `SKILL.md`: runtime instructions for AI assistants
- `references/engines`: audience, angle, scene, style, layout, and variation rules
- `references/templates`: JSON schemas and reusable prompt templates
- `scripts/compile_creatives.py`: deterministic local compiler from product JSON to creative plan JSON

## Minimal Usage

```bash
python .claude/skills/facebook-ad-creative/scripts/compile_creatives.py examples/beauty-serum.json
```

## Output

The compiler outputs structured JSON with:

- creative plans
- universal prompts
- GPT Image 2 prompts
- Nano Banana prompts
- diversity and quality checks

