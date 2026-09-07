#!/usr/bin/env python3
"""
Compile a product brief into structured Meta/Facebook ad creative plans.

This script is deterministic and does not call any image API. It is intended
to give agents and humans a stable prompt-planning layer before image creation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


ANGLES = [
    ("Pain Solution", "Show the product resolving a specific daily frustration."),
    ("Outcome Led", "Lead with the desired result and emotional payoff."),
    ("UGC Native", "Make the creative feel like a real customer snapshot."),
    ("Social Proof", "Use review-style framing and credibility cues."),
    ("Feature Benefit", "Translate concrete features into buyer benefits."),
    ("Problem Solution", "Contrast the problem moment with the product solution."),
    ("Gift", "Frame the product as a thoughtful, easy gift."),
    ("Offer", "Highlight value, bundle, discount, or low-friction purchase."),
    ("Premium Minimal", "Use refined minimal visuals for perceived quality."),
    ("Lifestyle", "Place the product inside an aspirational daily routine."),
]

SCENES = [
    "studio product hero on a clean background",
    "UGC-style home snapshot with natural light",
    "morning routine scene",
    "office desk or commute moment",
    "gift unboxing moment",
    "before and after split scene",
    "lifestyle scene in a real home",
    "close-up product-in-use scene",
    "organized flat lay with product and props",
    "mobile-native social post composition",
]

STYLES = [
    "high-conversion Facebook ad style",
    "UGC native realistic style",
    "minimal ecommerce style",
    "premium editorial style",
    "lifestyle natural-light style",
    "product plus callout style",
    "infographic benefit style",
    "split-screen comparison style",
    "review card style",
    "fresh western localized ad style",
]

LAYOUTS = [
    "Meta ASC V1: top headline, center product, bottom CTA",
    "Social Proof Layout: product plus review card",
    "Benefit Focus Layout: product hero with 2-3 callouts",
    "Transformation Split Layout: before/result comparison",
    "Problem Solution Layout: problem cue plus product solution",
    "UGC Native Layout: phone-shot framing with minimal overlay",
    "Product Callout Layout: clean product hero with labels",
    "Lifestyle Story Layout: product embedded in a daily moment",
    "Comparison Layout: old way versus new way",
    "Quote Review Card Layout: short review quote with product",
]

DEFAULT_NEGATIVES = [
    "avoid cluttered composition",
    "avoid tiny product placement",
    "avoid excessive text overlay",
    "avoid unreadable typography",
    "avoid unrealistic hands, faces, or anatomy",
    "avoid over-processed AI look",
    "avoid unrelated background objects",
    "avoid repeating the same template across the batch",
]

CATEGORY_AUDIENCES = {
    "beauty": ["skincare beginners", "busy professionals", "ingredient-aware shoppers"],
    "skincare": ["skincare beginners", "busy professionals", "ingredient-aware shoppers"],
    "pet": ["pet parents", "small apartment pet owners", "comfort-focused pet buyers"],
    "home": ["new homeowners", "renters", "organization seekers"],
    "kitchen": ["home cooks", "meal prep users", "busy families"],
    "apparel": ["comfort seekers", "style-conscious shoppers", "occasion shoppers"],
    "electronics": ["productivity users", "commuters", "tech gift buyers"],
    "health": ["routine builders", "wellness shoppers", "active lifestyle buyers"],
    "gift": ["gift buyers", "holiday shoppers", "last-minute shoppers"],
}


def load_input(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize(data: Dict[str, Any]) -> Dict[str, Any]:
    required = ["product_name", "product_category", "product_description"]
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    defaults = {
        "key_features": [],
        "benefits": [],
        "target_audiences": [],
        "audience_location": "United States",
        "price_positioning": "mid-range",
        "brand_tone": "clear, practical, trustworthy",
        "visual_style_preference": [],
        "banned_elements": [],
        "platform": "facebook",
        "aspect_ratio": "4:5",
        "language": "en",
        "generation_count": 4,
        "campaign_goal": "purchase",
        "awareness_stage": "cold",
        "interests": [],
        "scene_preferences": [],
        "angle_preferences": [],
        "text_overlay_mode": "light",
        "cta_mode": "soft",
        "offer_info": "",
        "seasonality": "",
        "compliance_notes": "",
        "competitor_style_notes": "",
        "variation_strength": "high",
    }
    normalized = {**defaults, **data}
    normalized["generation_count"] = max(1, min(int(normalized["generation_count"]), 24))
    return normalized


def infer_audiences(data: Dict[str, Any]) -> List[str]:
    if data["target_audiences"]:
        return data["target_audiences"]
    category = data["product_category"].lower()
    for key, audiences in CATEGORY_AUDIENCES.items():
        if key in category:
            return audiences
    return ["broad ecommerce shoppers", "problem-aware consumers", "gift buyers"]


def cycle(values: List[Any], index: int) -> Any:
    return values[index % len(values)]


def choose_angles(data: Dict[str, Any]) -> List[Any]:
    preferred = data.get("angle_preferences") or []
    mapped = [(item, f"User-preferred angle: {item}") for item in preferred]
    return mapped + ANGLES


def choose_scenes(data: Dict[str, Any]) -> List[str]:
    return list(data.get("scene_preferences") or []) + SCENES


def choose_styles(data: Dict[str, Any]) -> List[str]:
    return list(data.get("visual_style_preference") or []) + STYLES


def build_copy(data: Dict[str, Any], angle_name: str, benefit: str, index: int) -> Dict[str, Any]:
    product = data["product_name"]
    mode = data["text_overlay_mode"]
    offer = data.get("offer_info", "")

    if mode == "none":
        return {"headline": "", "subheadline": "", "bullets": [], "cta": ""}

    headline_templates = [
        f"Meet {product}",
        f"{benefit}",
        f"A better way to use {product}",
        f"Built for everyday {data['product_category']}",
        f"Make it easier with {product}",
    ]
    cta = "" if data["cta_mode"] == "none" else ("Shop Now" if data["cta_mode"] == "direct" else "See Why")
    if angle_name == "Offer" and offer:
        cta = "Claim Offer"

    bullets = data["key_features"][:3] if mode in ["standard", "heavy"] else data["key_features"][:1]
    return {
        "headline": cycle(headline_templates, index),
        "subheadline": offer or data["product_description"][:90],
        "bullets": bullets,
        "cta": cta,
    }


def build_audience_scene_bridge(data: Dict[str, Any], audience: str, scene: str, benefit: str, index: int) -> Dict[str, Any]:
    moments = ["a recognizable daily friction point", "the moment the product is selected for use", "active product use", "the immediate payoff after use"]
    camera = ["close mobile-feed product-and-action framing", "eye-level contextual medium shot", "hands-and-product detail view", "product-led environmental hero shot"]
    return {
        "use_moment": cycle(moments, index),
        "visible_behavior": f"Show the product being selected or used to achieve {benefit}",
        "environment_cues": [scene, f"context appropriate to {audience}", "credible everyday details"],
        "prop_cues": ["only use-case-relevant props", "keep props subordinate to the product"],
        "casting_direction": f"Use a person only when their action clarifies the use case for {audience}; avoid demographic stereotypes",
        "camera_language": cycle(camera, index),
        "copy_tone": f"{data['brand_tone']} language for a {data['awareness_stage']}-awareness audience",
        "why_it_fits": f"This moment connects {audience} with {benefit} through visible product use in {scene}.",
    }


def universal_prompt(data: Dict[str, Any], plan: Dict[str, Any]) -> str:
    copy = plan["copy"]
    bridge = plan["audience_scene_bridge"]
    banned = data["banned_elements"] + DEFAULT_NEGATIVES
    description = data["product_description"].rstrip(".")
    angle_rationale = plan["angle_rationale"].rstrip(".")
    return (
        f"Create a Meta/Facebook ad image for {data['product_name']}. "
        f"Product description: {description}. "
        f"Target audience: {plan['target_audience']} in {data['audience_location']}. "
        f"Interest cues: {', '.join(plan['interest_cues'])}. "
        f"Creative angle: {plan['angle']} - {angle_rationale}. "
        f"Audience-scene bridge: use moment {bridge['use_moment']}; visible behavior {bridge['visible_behavior']}; environment cues {', '.join(bridge['environment_cues'])}; prop cues {', '.join(bridge['prop_cues'])}; casting direction {bridge['casting_direction']}; camera language {bridge['camera_language']}; copy tone {bridge['copy_tone']}; rationale {bridge['why_it_fits']} "
        f"Scene: {plan['scene']}. Visual style: {plan['style']}. "
        f"Layout: {plan['layout']}. Main benefit: {plan['core_benefit']}. "
        f"Use aspect ratio {data['aspect_ratio']} for mobile-first browsing. "
        f"On-image copy mode: {data['text_overlay_mode']}. Target copy language: {data['language']}. "
        f"Headline: '{copy['headline']}'. Subheadline: '{copy['subheadline']}'. "
        f"Bullets: {', '.join(copy['bullets'])}. CTA: '{copy['cta']}'. "
        + (
            "Render no words, letters, logos, badges, CTA controls, or decorative pseudo-text. "
            if data["text_overlay_mode"] == "none"
            else "Rendering the supplied copy is required. Preserve exact spelling and use a clear mobile-first hierarchy, natural line breaks, strong contrast, safe margins, and layout-appropriate density near or below 20 percent of the canvas. Do not invent extra copy, prices, discounts, ratings, brands, claims, or offers. "
        )
        +
        f"Brand tone: {data['brand_tone']}. Campaign goal: {data['campaign_goal']}. "
        f"{plan['difference_statement']} "
        f"Negative constraints: {', '.join(banned)}."
    )


def build_creatives(data: Dict[str, Any]) -> Dict[str, Any]:
    audiences = infer_audiences(data)
    angles = choose_angles(data)
    scenes = choose_scenes(data)
    styles = choose_styles(data)
    benefits = data["benefits"] or data["key_features"] or ["clear product value"]
    interests = data["interests"] or [data["product_category"], data["campaign_goal"], data["price_positioning"]]

    creatives = []
    used_combos = set()
    for i in range(data["generation_count"]):
        angle_name, angle_rationale = cycle(angles, i)
        scene = cycle(scenes, i * 2 if data["variation_strength"] == "high" else i)
        style = cycle(styles, i * 3 if data["variation_strength"] == "high" else i)
        layout = cycle(LAYOUTS, i * 5 if data["variation_strength"] == "high" else i)
        combo = (scene, style, layout)
        if combo in used_combos:
            layout = cycle(LAYOUTS, i * 5 + 1)
            combo = (scene, style, layout)
        used_combos.add(combo)

        target_audience = cycle(audiences, i)
        core_benefit = cycle(benefits, i)
        bridge = build_audience_scene_bridge(data, target_audience, scene, core_benefit, i)
        plan = {
            "target_audience": target_audience,
            "interest_cues": [cycle(interests, i), cycle(interests, i + 1), data["product_category"]],
            "pain_point": f"{target_audience} need a simpler way to get {core_benefit}",
            "core_benefit": core_benefit,
            "angle": angle_name,
            "angle_rationale": angle_rationale,
            "scene": scene,
            "style": style,
            "layout": layout,
            "audience_scene_bridge": bridge,
            "copy": build_copy(data, angle_name, core_benefit, i),
            "difference_statement": (
                f"This variation focuses on {angle_name} for {target_audience}, "
                f"using a distinct {scene}, {style}, and {layout} compared with the other creatives in this batch."
            ),
        }
        prompt = universal_prompt(data, plan)
        creatives.append(
            {
                "id": f"creative_{i + 1:02d}",
                "creative_plan": plan,
                "model_prompts": {
                    "universal": prompt,
                    "gpt_image_2": (
                        "High-quality commercial ad image with precise layout control, realistic product rendering, "
                        "clean readable typography, and strong mobile feed clarity. Treat text mode and exact copy as hard constraints. " + prompt
                    ),
                    "nano_banana": (
                        "Direct image prompt: clear product hero, distinct visual concept, natural commercial lighting, "
                        "controlled readable ad typography and no clutter. Treat text mode and exact copy as hard constraints. " + prompt
                    ),
                    "negative_constraints": data["banned_elements"] + DEFAULT_NEGATIVES,
                },
            }
        )

    checks = [
        f"Generated {len(creatives)} creative variants.",
        "Scene-style-layout combinations are rotated to reduce same-template outputs.",
        "Each prompt includes an explicit difference statement.",
        "Text overlay is constrained by the selected text_overlay_mode.",
    ]
    if "health" in data["product_category"].lower() or data.get("compliance_notes"):
        checks.append("Compliance caution: avoid medical claims, guaranteed outcomes, and sensitive personal implication.")

    return {
        "input_summary": {
            "product_name": data["product_name"],
            "product_category": data["product_category"],
            "generation_count": data["generation_count"],
            "aspect_ratio": data["aspect_ratio"],
            "variation_strength": data["variation_strength"],
        },
        "creative_plans": creatives,
        "quality_checks": checks,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: compile_creatives.py <input.json>", file=sys.stderr)
        return 2
    input_path = Path(sys.argv[1])
    data = normalize(load_input(input_path))
    output = build_creatives(data)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
