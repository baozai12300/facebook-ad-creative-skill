#!/usr/bin/env python3
"""
Compile a product brief into structured Meta/Facebook ad creative plans (v2).

This script is deterministic and does not call any image API. It is intended
to give agents and humans a stable prompt-planning layer before image creation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


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
    "phone case": ["device protection shoppers", "style-focused phone users", "minimal accessory buyers", "MagSafe users", "case refresh shoppers", "gift buyers"],
    "mobile accessories": ["device protection shoppers", "style-focused phone users", "minimal accessory buyers", "MagSafe users", "case refresh shoppers", "gift buyers"],
    "smartphone accessories": ["device protection shoppers", "style-focused phone users", "minimal accessory buyers", "MagSafe users", "case refresh shoppers", "gift buyers"],
    "phone accessories": ["device protection shoppers", "style-focused phone users", "minimal accessory buyers", "MagSafe users", "case refresh shoppers", "gift buyers"],
    "iphone case": ["device protection shoppers", "style-focused phone users", "minimal accessory buyers", "MagSafe users", "case refresh shoppers", "gift buyers"],
    "magsafe": ["MagSafe users", "device protection shoppers", "minimal accessory buyers", "style-focused phone users", "case refresh shoppers", "gift buyers"],
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

PLACEMENTS = {
    "feed": ("4:5", "1080x1350", "center 80%", "Keep all critical product, text, and logo content inside the center 80%; do not place key elements against an edge."),
    "square_feed": ("1:1", "1080x1080", "centered safe field", "Build a native square composition with generous edge clearance; never crop a 4:5 Feed design."),
    "story": ("9:16", "1080x1920", "middle 70%", "Keep the product, headline, and logo inside the middle safe field, away from top and bottom interface zones."),
    "reels": ("9:16", "1080x1920", "upper-middle field", "Place product, headline, and logo in the upper-middle safe field; keep the bottom region visually quiet for controls."),
    "carousel": ("1:1", "1080x1080", "centered safe field", "Use one primary message per card in a native 1:1 composition; never crop a Feed version."),
}

LAYOUT_PROFILES = {
    "product_hero": ("L1 Product Hero", "center or right-center, 52–66% of canvas height", "upper-left safe zone", "one short support line", "upper-left", "headline → product → material detail"),
    "benefit_focus": ("L2 Benefit Focus", "right-center, 48–60% of canvas height", "upper-left safe zone", "up to two labels beside, never over, the product", "left and upper-left", "headline → product → benefits"),
    "problem_solution": ("L3 Problem → Solution Split", "fully inside the brighter solution side, about 48% of canvas height", "top safe zone", "one short phrase per side", "around the divider and product", "problem → product solution → outcome"),
    "lifestyle_story": ("L4 Lifestyle Story", "in natural use near center-right, visually prominent at 35–45% of frame", "environmental negative space", "none", "around the headline and product", "use action → product → outcome"),
    "ugc_native": ("L5 UGC Native Static", "in hand or in use near center, recognizable at mobile size", "top safe zone", "none", "behind the headline", "real action → product → headline"),
    "review_proof": ("L6 Review / Proof Card", "center-right and primary, 50–60% of canvas height", "upper-left safe zone", "one supplied proof card under 25% of canvas", "between product and proof", "product → supplied proof → headline"),
    "offer_value": ("L7 Offer / Value", "large and central, 55–65% of canvas height", "upper safe zone", "one supplied offer chip smaller than product", "around product and offer", "product → offer → optional CTA"),
    "comparison": ("L8 Comparison", "dominant on the preferred side of a clean two-region comparison", "top safe zone", "one supplied-fact label per side", "around divider and labels", "old method → product-led method → benefit"),
    "minimal_editorial": ("L9 Minimal Editorial", "center-lower or right-center, 38–52% of canvas height", "upper negative space", "none", "55–70% of canvas", "product → material detail → optional headline"),
    "infographic_lite": ("L10 Infographic Lite", "center, 45–55% of canvas height", "upper-center safe zone", "up to two supplied-fact callouts", "between product and labels", "headline → product → supplied facts"),
}

VISUAL_DNA = {
    "clean_ecommerce": ("Clean Ecommerce", "soft commercial key and fill", "clean product-forward 3/4 view", "simple tonal surface", "restrained brand-compatible palette", "precise surface detail", "sparse structured graphics"),
    "ugc_native": ("UGC Native", "natural window or practical room light", "close phone-shot framing with believable imperfection", "lived-in environment with controlled clutter", "natural lightly processed color", "honest everyday texture", "headline only when needed"),
    "premium_editorial": ("Premium Editorial", "sculpted dimensional light with controlled shadow", "deliberate premium crop and lens feel", "refined texture or architectural simplicity", "restrained premium palette", "emphasized finish and edge detail", "very little or no graphics"),
    "lifestyle_natural": ("Lifestyle Natural", "soft believable environmental daylight", "contextual medium shot or product-in-use close-up", "relevant real-world environment", "warm neutral palette", "natural product and environmental textures", "copy only in existing negative space"),
    "benefit_callout": ("Benefit Callout", "clean product-legible commercial light", "clear hero or 3/4 view", "low-noise background", "controlled high-contrast palette", "clear supplied feature detail", "no more than two supplied-fact callouts"),
    "comparison": ("Comparison", "matched light with a brighter product-led side", "matched framing across two regions", "clean structural split", "controlled old/new contrast", "consistent realistic rendering", "one short phrase per side at most"),
}

ANGLE_HYPOTHESES = [
    ("Premium Product Hero", "clarity", "product_hero", "premium_editorial", "clean studio product hero"),
    ("Problem → Solution", "problem", "problem_solution", "comparison", "truthful old-way versus product-led solution"),
    ("Product Demonstration", "lifestyle", "lifestyle_story", "lifestyle_natural", "close product-in-use moment"),
    ("Feature → Benefit", "benefit", "benefit_focus", "benefit_callout", "clean contextual product demonstration"),
    ("UGC Real Use", "lifestyle", "ugc_native", "ugc_native", "everyday UGC-style use moment"),
    ("Lifestyle / Identity", "lifestyle", "lifestyle_story", "lifestyle_natural", "believable daily routine"),
    ("Objection Handling", "comparison", "comparison", "clean_ecommerce", "visual demonstration resolving a practical purchase concern"),
    ("Minimal Product Clarity", "clarity", "minimal_editorial", "premium_editorial", "refined minimal product study"),
    ("Benefit / Outcome", "benefit", "benefit_focus", "clean_ecommerce", "product-led outcome moment"),
    ("Infographic Feature", "benefit", "infographic_lite", "benefit_callout", "clean product hero with supplied feature evidence"),
]


def load_input(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError("Input must be a JSON object")
    return payload


def normalize(data: Dict[str, Any]) -> Dict[str, Any]:
    required = ["product_name", "product_category", "product_description"]
    missing = [key for key in required if not isinstance(data.get(key), str) or not data[key].strip()]
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
        "platform": "meta",
        "placement": "feed",
        "aspect_ratio": "",
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
        "social_proof": "",
        "seasonality": "",
        "compliance_notes": "",
        "competitor_style_notes": "",
        "variation_strength": "high",
        "reference_image": "",
        "product_identity_constraints": [],
    }
    normalized = {**defaults, **data}
    list_fields = [
        "key_features", "benefits", "target_audiences", "visual_style_preference",
        "banned_elements", "interests", "scene_preferences", "angle_preferences",
        "product_identity_constraints",
    ]
    for key in list_fields:
        value = normalized[key]
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise ValueError(f"Field '{key}' must be an array of strings")

    allowed_values = {
        "price_positioning": {"budget", "mid-range", "premium", "luxury"},
        "platform": {"facebook", "instagram", "meta"},
        "placement": set(PLACEMENTS),
        "campaign_goal": {"awareness", "traffic", "engagement", "lead", "purchase", "retention", "retargeting", "launch", "offer"},
        "awareness_stage": {"cold", "warm", "hot", "mixed"},
        "text_overlay_mode": {"none", "light", "standard", "heavy"},
        "cta_mode": {"none", "soft", "direct"},
        "variation_strength": {"low", "medium", "high"},
    }
    for key, allowed in allowed_values.items():
        if normalized[key] not in allowed:
            raise ValueError(f"Invalid {key}: {normalized[key]!r}; expected one of {sorted(allowed)}")

    count = normalized["generation_count"]
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 24:
        raise ValueError("generation_count must be an integer from 1 to 24")
    normalized["aspect_ratio"] = normalized["aspect_ratio"] or PLACEMENTS[normalized["placement"]][0]
    if normalized["aspect_ratio"] not in {"1:1", "4:5", "9:16", "16:9"}:
        raise ValueError("aspect_ratio must be one of 1:1, 4:5, 9:16, 16:9")
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


def _custom_angle(name: str) -> Dict[str, str]:
    lowered = name.lower()
    if any(word in lowered for word in ("ugc", "testimonial", "review", "真实")):
        kind, layout, style = "lifestyle", "ugc_native", "ugc_native"
    elif any(word in lowered for word in ("problem", "solution", "before", "after", "痛点", "对比")):
        kind, layout, style = "problem", "problem_solution", "comparison"
    elif any(word in lowered for word in ("texture", "feature", "benefit", "ingredient", "功能", "卖点")):
        kind, layout, style = "benefit", "benefit_focus", "benefit_callout"
    elif any(word in lowered for word in ("premium", "minimal", "hero", "高级", "极简")):
        kind, layout, style = "clarity", "minimal_editorial", "premium_editorial"
    else:
        kind, layout, style = "lifestyle", "lifestyle_story", "lifestyle_natural"
    return {"name": name, "kind": kind, "layout": layout, "style": style, "scene": "a use moment that visibly expresses this supplied angle"}


def choose_angles(data: Dict[str, Any]) -> List[Dict[str, str]]:
    angles = [{**_custom_angle(name), "supplied_preference": True} for name in data["angle_preferences"]]
    core = [
        {"name": name, "kind": kind, "layout": layout, "style": style, "scene": scene}
        for name, kind, layout, style, scene in ANGLE_HYPOTHESES
    ]
    angles.extend(core[:4])
    if data["social_proof"]:
        angles.append({"name": "Supplied Social Proof", "kind": "proof", "layout": "review_proof", "style": "clean_ecommerce", "scene": "product hero supported by the supplied proof"})
    if data["offer_info"]:
        angles.append({"name": "Supplied Offer / Value", "kind": "offer", "layout": "offer_value", "style": "clean_ecommerce", "scene": "product-led value presentation"})
    angles.extend(core[4:])
    unique, seen = [], set()
    for angle in angles:
        key = angle["name"].lower()
        if key not in seen:
            unique.append({**angle, "score": score_angle(data, angle)})
            seen.add(key)
    return sorted(unique, key=lambda item: (-item["score"], item["name"]))


def score_angle(data: Dict[str, Any], angle: Dict[str, str]) -> int:
    """Rank eligible angle hypotheses from campaign and product evidence."""
    name = angle["name"]
    kind = angle["kind"]
    score = 10
    if angle.get("supplied_preference"):
        score += 35

    awareness_weights = {
        "cold": {"Premium Product Hero": 28, "Problem → Solution": 26, "Product Demonstration": 24, "Feature → Benefit": 22, "UGC Real Use": 20},
        "warm": {"Objection Handling": 28, "Feature → Benefit": 26, "Benefit / Outcome": 22, "Product Demonstration": 18, "Supplied Social Proof": 30},
        "hot": {"Supplied Offer / Value": 34, "Objection Handling": 28, "Premium Product Hero": 24, "Minimal Product Clarity": 22, "Supplied Social Proof": 30},
        "mixed": {"Premium Product Hero": 22, "Problem → Solution": 20, "Feature → Benefit": 20, "Product Demonstration": 18},
    }
    score += awareness_weights[data["awareness_stage"]].get(name, 0)

    goal_weights = {
        "purchase": {"clarity": 12, "problem": 10, "benefit": 9, "lifestyle": 7, "offer": 12},
        "retargeting": {"offer": 16, "comparison": 13, "proof": 13, "clarity": 10},
        "offer": {"offer": 20, "clarity": 10},
        "launch": {"clarity": 15, "benefit": 12, "lifestyle": 8},
        "awareness": {"lifestyle": 13, "problem": 11, "clarity": 9},
        "traffic": {"problem": 10, "benefit": 9, "lifestyle": 8},
        "engagement": {"lifestyle": 12, "comparison": 8},
        "lead": {"problem": 11, "benefit": 10, "proof": 9},
        "retention": {"benefit": 11, "lifestyle": 10, "proof": 8},
    }
    score += goal_weights.get(data["campaign_goal"], {}).get(kind, 0)

    if data["price_positioning"] in {"premium", "luxury"}:
        score += {"Premium Product Hero": 24, "Minimal Product Clarity": 22}.get(name, 0)
        if angle["style"] == "premium_editorial":
            score += 8
    elif data["price_positioning"] == "budget":
        score += {"Feature → Benefit": 15, "Problem → Solution": 12, "Supplied Offer / Value": 14}.get(name, 0)

    if data["benefits"] or data["key_features"]:
        score += {"benefit": 8, "problem": 5, "comparison": 4}.get(kind, 0)
    if kind == "offer":
        score += 15 if data["offer_info"] else -1000
        if data["awareness_stage"] == "cold":
            score -= 15
    if kind == "proof":
        score += 15 if data["social_proof"] else -1000
        if data["awareness_stage"] == "cold":
            score -= 10
    if any(alias in data["product_category"].lower() for alias in ("phone case", "mobile accessories", "smartphone accessories", "phone accessories", "iphone case", "magsafe")):
        score += {"Product Demonstration": 10, "Lifestyle / Identity": 8, "Minimal Product Clarity": 7}.get(name, 0)
    return score


def select_angles(data: Dict[str, Any], count: int) -> List[Dict[str, str]]:
    ranked = choose_angles(data)
    pool_size = {"low": min(2, len(ranked)), "medium": min(max(4, count // 2), len(ranked)), "high": len(ranked)}[data["variation_strength"]]
    pool = ranked[:pool_size]
    return [pool[index % len(pool)] for index in range(count)]


def benefit_phrase(benefit: str, data: Dict[str, Any]) -> str:
    """Convert supplied benefit wording into a short, claim-safe ad phrase."""
    cleaned = " ".join(benefit.strip().rstrip(".!?").split())
    lowered = cleaned.lower()
    exact = {
        "reduce cable switching": "Fewer Cable Swaps",
        "connect more desk accessories": "More Ports. One Hub.",
        "brighter-looking skin": "Brighter-Looking Skin",
        "more even-looking tone": "More Even-Looking Tone",
        "hydrated finish": "Daily Hydration",
        "faster meal prep": "Faster Meal Prep",
        "less mess": "Less Mess",
        "hands-free organization": "Hands-Free Organization",
    }
    if lowered in exact:
        return exact[lowered]
    if lowered.startswith("reduce "):
        subject = cleaned[7:].strip()
        prefix = "Fewer" if any(word in subject.lower() for word in ("switch", "swap", "step", "cable", "click")) else "Less"
        phrase = f"{prefix} {subject}"
    elif lowered.startswith("connect more "):
        subject = cleaned[13:].strip()
        suffix = "One Hub" if "hub" in data["product_name"].lower() or "hub" in data["product_category"].lower() else "One Setup"
        phrase = f"More {subject}. {suffix}."
    else:
        for prefix in ("helps ", "help ", "get ", "enjoy ", "achieve ", "make "):
            if lowered.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break
        phrase = cleaned.title()
    words = phrase.split()
    return " ".join(words[:7]).rstrip(".,") + ("." if phrase.endswith(".") else "")


def _short_product_name(name: str) -> str:
    words = name.split()
    return " ".join(words[:6])


def _short_fact(value: str, data: Dict[str, Any]) -> str:
    return benefit_phrase(value, data)


def build_copy(data: Dict[str, Any], angle: Dict[str, str], benefit: str) -> Dict[str, Any]:
    mode = data["text_overlay_mode"]
    if mode == "none":
        return {"headline": "", "support": "", "callouts": [], "cta": ""}

    phrase = benefit_phrase(benefit, data)
    layout = angle["layout"]
    headline = {
        "clarity": f"Meet {_short_product_name(data['product_name'])}",
        "problem": phrase,
        "lifestyle": "Ready for Every Day",
        "benefit": phrase,
        "comparison": phrase,
        "proof": data["social_proof"],
        "offer": f"Meet {_short_product_name(data['product_name'])}",
    }.get(angle["kind"], phrase)
    support = ""
    callouts: List[str] = []

    # Layout owns density; text_overlay_mode only caps it.
    if layout in {"ugc_native", "lifestyle_story"}:
        pass
    elif layout in {"product_hero", "minimal_editorial"} and mode in {"standard", "heavy"}:
        support = _short_fact(benefit, data) if headline.lower() != phrase.lower() else ""
    elif layout in {"benefit_focus", "infographic_lite"} and mode in {"standard", "heavy"}:
        callouts = [_short_fact(item, data) for item in data["key_features"][:2]]
    elif layout in {"problem_solution", "comparison"} and mode in {"standard", "heavy"}:
        facts = data["benefits"] or data["key_features"]
        callouts = [_short_fact(item, data) for item in facts[:2]]
    elif layout == "offer_value":
        support = data["offer_info"]
    elif layout == "review_proof":
        headline = data["social_proof"]

    cta = ""
    if layout == "offer_value" and mode == "heavy" and data["cta_mode"] != "none":
        cta = "Shop Now" if data["cta_mode"] == "direct" else "Learn More"
    return {"headline": headline, "support": support, "callouts": callouts[:2], "cta": cta}


def build_audience_scene_bridge(data: Dict[str, Any], audience: str, scene: str, benefit: str, index: int) -> Dict[str, Any]:
    moments = ["the moment the product is selected for use", "active product use during a familiar routine", "the immediate practical payoff after use", "a recognizable friction point just before use"]
    behaviors = [f"selecting and using the product to achieve {benefit}", f"handling the product naturally while pursuing {benefit}", f"showing the product-led result: {benefit}"]
    cameras = ["tight product-and-action framing", "eye-level contextual medium shot", "hands-and-product detail", "product-led environmental hero"]
    return {
        "use_moment": cycle(moments, index),
        "visible_behavior": cycle(behaviors, index),
        "environment_cues": [scene, f"credible context for {audience}", "only relevant everyday details"],
        "prop_cues": ["use-case-relevant props only", "props subordinate to the product"],
        "casting_direction": "Use a person only when their action clarifies the use case; avoid stereotypes.",
        "camera_language": cycle(cameras, index),
        "copy_tone": f"{data['brand_tone']} for a {data['awareness_stage']} audience",
    }


def select_scene(data: Dict[str, Any], angle: Dict[str, str], index: int) -> str:
    if data["scene_preferences"]:
        preference_index = 0 if data["variation_strength"] == "low" else index % len(data["scene_preferences"])
        return data["scene_preferences"][preference_index]
    category = data["product_category"].lower()
    mobile_scenes = [
        "commute with the protected phone in hand", "organized desk with phone and case",
        "mirror selfie showing the case", "cafe table everyday carry", "car mount use",
        "MagSafe wireless charging", "travel carry moment", "everyday carry flat lay",
    ]
    if any(alias in category for alias in ("phone case", "mobile accessories", "smartphone accessories", "phone accessories", "iphone case", "magsafe")):
        scene_index = 0 if data["variation_strength"] == "low" else index % len(mobile_scenes)
        return f"{mobile_scenes[scene_index]}; {angle['scene']}"
    category_scene = "believable everyday environment"
    for keys, value in [
        (("beauty", "skincare"), "morning vanity or bathroom routine"),
        (("kitchen",), "clean food-prep counter during use"),
        (("electronics",), "modern desk, commute, or creator setup"),
        (("pet",), "comfortable real-home pet interaction"),
        (("apparel",), "natural getting-ready or on-the-go moment"),
        (("home",), "organized lived-in home context"),
    ]:
        if any(key in category for key in keys):
            category_scene = value
            break
    return angle["scene"] if angle["kind"] == "clarity" else f"{category_scene}; {angle['scene']}"


def preferred_visual_styles(data: Dict[str, Any]) -> List[str]:
    mapped = []
    for value in data["visual_style_preference"]:
        lowered = value.lower()
        if any(word in lowered for word in ("ugc", "phone-shot", "native")):
            key = "ugc_native"
        elif any(word in lowered for word in ("premium", "editorial", "luxury", "minimal")):
            key = "premium_editorial"
        elif any(word in lowered for word in ("benefit", "callout", "infographic")):
            key = "benefit_callout"
        elif any(word in lowered for word in ("lifestyle", "natural")):
            key = "lifestyle_natural"
        elif "comparison" in lowered or "split" in lowered:
            key = "comparison"
        else:
            key = "clean_ecommerce"
        if key not in mapped:
            mapped.append(key)
    return mapped


def select_visual_style(data: Dict[str, Any], angle: Dict[str, str], index: int) -> str:
    preferences = preferred_visual_styles(data)
    if preferences:
        if data["variation_strength"] == "low":
            return preferences[0]
        if data["variation_strength"] == "medium" and index % 2 == 0:
            return preferences[index % len(preferences)]
        if data["variation_strength"] == "high" and index % 3 != 2:
            return preferences[index % len(preferences)]
    if data["price_positioning"] in {"premium", "luxury"} and angle["kind"] == "clarity":
        return "premium_editorial"
    return angle["style"]


def product_identity_instruction(data: Dict[str, Any]) -> str:
    locked = ", ".join(data["product_identity_constraints"]) or "silhouette, proportions, colorway, materials, packaging, logo position, controls, and distinctive details"
    if data["reference_image"]:
        return f"Preserve the supplied product reference exactly—lock {locked}. Do not redesign the SKU."
    return f"Preserve the described product identity—keep {locked} consistent. Do not invent a different SKU or packaging."


def text_instruction(data: Dict[str, Any], copy: Dict[str, Any], headline_zone: str) -> str:
    if data["text_overlay_mode"] == "none":
        return "No rendered words, letters, badges, buttons, added logos, or pseudo-text; preserve only native text printed on the product."
    parts = [f"Render headline exactly: \"{copy['headline']}\" in the {headline_zone}"]
    if copy["support"]:
        parts.append(f"support line exactly: \"{copy['support']}\"")
    if copy["callouts"]:
        parts.append("callouts exactly: " + "; ".join(f'\"{item}\"' for item in copy["callouts"]))
    if copy["cta"]:
        parts.append(f"optional CTA exactly: \"{copy['cta']}\"")
    parts.append(f"use {data['language']} only, strong contrast, natural line breaks, safe margins, and no extra copy")
    return "; ".join(parts) + "."


def universal_prompt(data: Dict[str, Any], plan: Dict[str, Any]) -> str:
    layout = plan["layout_profile"]
    dna = plan["visual_dna"]
    negatives = plan["negative_constraints"]
    return "\n\n".join([
        f"Create a {data['aspect_ratio']} Meta ecommerce ad image for {data['placement'].replace('_', ' ')}.",
        f"PRODUCT: {product_identity_instruction(data)}",
        f"SCENE: {plan['scene']}. Show {plan['audience_scene_bridge']['visible_behavior']}; use only relevant props subordinate to the product.",
        f"PLACEMENT: {plan['placement_instruction']}",
        f"COMPOSITION: Product {layout['product_position']}. Headline zone: {layout['headline_zone']}. Support zone: {layout['support_zone']}. Keep {layout['negative_space']} uncluttered. Visual flow: {layout['visual_flow']}.",
        f"LOOK: {dna['lighting']}. {dna['camera_language']}. {dna['background_character']}. {dna['color_mood']}. {dna['material_treatment']}. High commercial realism. {dna['graphic_treatment']}.",
        f"TEXT: {text_instruction(data, plan['copy'], layout['headline_zone'])}",
        "AVOID: " + "; ".join(negatives) + ".",
    ])


def headline_is_natural(headline: str, angle_kind: str) -> bool:
    if angle_kind == "proof":
        return bool(headline.strip())
    lowered = " ".join(headline.lower().split())
    broken = ("a simpler way to get ", "make connect ", "make reduce ", "make get ", " easier easier")
    word_count = len(headline.replace(".", " ").split())
    return bool(headline.strip()) and not any(pattern in lowered for pattern in broken) and 2 <= word_count <= 7


def quality_gate(data: Dict[str, Any], plan: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    findings = []
    word_count = len(prompt.split())
    if word_count > 240:
        findings.append(f"render prompt exceeds compact budget ({word_count} words)")
    if data["text_overlay_mode"] == "none" and any(plan["copy"].values()):
        findings.append("no-text mode contains copy")
    if data["text_overlay_mode"] == "none" and "Render headline exactly" in prompt:
        findings.append("no-text prompt contains a headline instruction")
    if len(plan["copy"]["callouts"]) > 2:
        findings.append("more than two benefit callouts")
    if plan["angle_kind"] == "proof" and not data["social_proof"]:
        findings.append("proof angle lacks supplied proof")
    if plan["angle_kind"] == "offer" and not data["offer_info"]:
        findings.append("offer angle lacks supplied offer")
    if plan["placement_instruction"] not in prompt:
        findings.append("placement safe-zone instruction missing from render prompt")
    if data["text_overlay_mode"] != "none" and not headline_is_natural(plan["copy"]["headline"], plan["angle_kind"]):
        findings.append("headline is empty, too long, or resembles broken template grammar")
    return {
        "pass": not findings,
        "findings": findings,
        "revised": False,
        "prompt_word_count": word_count,
        "checks": ["product fidelity", "one-glance message", "product prominence", "layout clarity", "copy accuracy", "placement safe-zone compiled", "claim integrity", "headline grammar", "prompt word budget"],
    }


def build_creatives(data: Dict[str, Any]) -> Dict[str, Any]:
    audiences = infer_audiences(data)
    angles = select_angles(data, data["generation_count"])
    benefits = data["benefits"] or data["key_features"] or [data["product_description"]]
    compliance_constraints = []
    if data["compliance_notes"]:
        compliance_constraints.append(data["compliance_notes"])
    if "health" in data["product_category"].lower():
        compliance_constraints.append("medical claims, guaranteed outcomes, or sensitive personal implications")
    negatives = list(dict.fromkeys(data["banned_elements"] + compliance_constraints + DEFAULT_NEGATIVES))
    placement_ratio, canvas, safe_composition, placement_note = PLACEMENTS[data["placement"]]
    creatives = []

    for index in range(data["generation_count"]):
        angle = angles[index]
        audience = cycle(audiences, index)
        benefit = cycle(benefits, index)
        scene = select_scene(data, angle, index)
        layout_values = LAYOUT_PROFILES[angle["layout"]]
        layout = dict(zip(["name", "product_position", "headline_zone", "support_zone", "negative_space", "visual_flow"], layout_values))
        selected_style = select_visual_style(data, angle, index)
        dna_values = VISUAL_DNA[selected_style]
        dna = dict(zip(["name", "lighting", "camera_language", "background_character", "color_mood", "material_treatment", "graphic_treatment"], dna_values))
        bridge = build_audience_scene_bridge(data, audience, scene, benefit, index)
        plan = {
            "angle_kind": angle["kind"],
            "scene": scene,
            "audience_scene_bridge": bridge,
            "layout_profile": layout,
            "visual_dna": dna,
            "copy": build_copy(data, angle, benefit),
            "negative_constraints": negatives,
            "placement_instruction": f"Safe composition: {safe_composition}. {placement_note}",
        }
        prompt = universal_prompt(data, plan)
        quality = quality_gate(data, plan, prompt)
        creative_id = f"C{index + 1:02d}"
        creatives.append({
            "id": creative_id,
            "creative_id": creative_id,
            "hypothesis": {
                "audience": audience,
                "awareness_stage": data["awareness_stage"],
                "objective": data["campaign_goal"],
                "angle": angle["name"],
                "core_benefit": benefit,
                "use_moment": bridge["use_moment"],
                "visible_behavior": bridge["visible_behavior"],
                "rationale": f"Express {benefit} through a {angle['name']} concept for {audience}.",
            },
            "placement_plan": {
                "placement": data["placement"], "aspect_ratio": data["aspect_ratio"], "canvas": canvas,
                "safe_composition": safe_composition, "adaptation_notes": placement_note,
                "native_ratio": placement_ratio,
            },
            "visual_plan": {
                "scene": scene, "audience_scene_bridge": bridge, "visual_dna": dna,
                "layout": layout["name"], "product_position": layout["product_position"],
                "headline_zone": layout["headline_zone"], "support_zone": layout["support_zone"],
                "negative_space": layout["negative_space"], "visual_flow": layout["visual_flow"],
                "text_mode": data["text_overlay_mode"], "copy": plan["copy"],
            },
            "render_prompt": prompt,
            "model_prompts": {
                "universal": prompt,
                "gpt_image_2": prompt + "\n\nRender the exact requested typography with precise alignment and no added text.",
                "nano_banana": prompt + "\n\nPrioritize product fidelity and composition; keep typography simple and exact.",
            },
            "negative_constraints": negatives,
            "quality_check": quality,
        })

    angle_count = len({item["hypothesis"]["angle"] for item in creatives})
    layout_count = len({item["visual_plan"]["layout"] for item in creatives})
    combo_count = len({(item["hypothesis"]["angle"], item["visual_plan"]["scene"], item["visual_plan"]["layout"]) for item in creatives})
    findings = []
    required_angles = min(len(creatives), {"low": 2, "medium": 3, "high": 4}[data["variation_strength"]])
    required_layouts = min(len(creatives), {"low": 1, "medium": 2, "high": 3}[data["variation_strength"]])
    if angle_count < required_angles:
        findings.append(f"angle diversity below required minimum ({angle_count}/{required_angles})")
    if layout_count < required_layouts:
        findings.append(f"layout diversity below required minimum ({layout_count}/{required_layouts})")
    if data["variation_strength"] == "high" and combo_count != len(creatives):
        findings.append("duplicate angle-scene-layout hypotheses detected")
    return {
        "schema_version": "2.0",
        "input_summary": {
            "product_name": data["product_name"], "product_category": data["product_category"],
            "generation_count": data["generation_count"], "placement": data["placement"],
            "aspect_ratio": data["aspect_ratio"], "variation_strength": data["variation_strength"],
        },
        "creative_plans": creatives,
        "quality_checks": {
            "pass": not findings and all(item["quality_check"]["pass"] for item in creatives),
            "findings": findings, "distinct_angles": angle_count, "distinct_layouts": layout_count,
            "distinct_hypothesis_combinations": combo_count,
        },
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: compile_creatives.py <input.json>", file=sys.stderr)
        return 2
    try:
        data = normalize(load_input(Path(sys.argv[1])))
        output = build_creatives(data)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
