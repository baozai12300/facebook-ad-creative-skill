#!/usr/bin/env python3
"""
Compile a product brief into structured Meta/Facebook ad creative plans (v2).

This script is deterministic and does not call any image API. It is intended
to give agents and humans a stable prompt-planning layer before image creation.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_NEGATIVES = [
    "no cluttered composition",
    "no tiny product",
    "no excessive text",
    "no unreadable typography",
    "no unrealistic anatomy",
    "no over-processed AI look",
    "no unrelated props",
    "no repeated batch template",
    "no unsupported claims, specs, proof, offers, or transformations",
]

CATEGORY_AUDIENCES = {
    "phone case": ["device protection shoppers", "style-focused phone users", "minimal accessory buyers", "MagSafe users", "case refresh shoppers", "gift buyers"],
    "mobile accessories": ["device protection shoppers", "style-focused phone users", "minimal accessory buyers", "MagSafe users", "case refresh shoppers", "gift buyers"],
    "smartphone accessories": ["device protection shoppers", "style-focused phone users", "minimal accessory buyers", "MagSafe users", "case refresh shoppers", "gift buyers"],
    "phone accessories": ["device protection shoppers", "style-focused phone users", "minimal accessory buyers", "MagSafe users", "case refresh shoppers", "gift buyers"],
    "iphone case": ["device protection shoppers", "style-focused phone users", "minimal accessory buyers", "MagSafe users", "case refresh shoppers", "gift buyers"],
    "magsafe": ["MagSafe users", "device protection shoppers", "minimal accessory buyers", "style-focused phone users", "case refresh shoppers", "gift buyers"],
    "beauty": ["skincare beginners", "busy professionals", "ingredient-aware shoppers", "premium skincare shoppers"],
    "skincare": ["skincare beginners", "busy professionals", "ingredient-aware shoppers", "premium skincare shoppers"],
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
    "product_hero": ("L1 Product Hero", "center or right-center, 52–66% of canvas height", "upper-left safe zone", "one short support line", "upper-left", "headline → product → material detail", "oversized editorial headline with a small caption", "asymmetric crop, thin rules, one restrained shape"),
    "benefit_focus": ("L2 Benefit Focus", "right-center, 48–60% of canvas height", "upper-left safe zone", "up to two labels beside, never over, the product", "left and upper-left", "headline → product → benefits", "bold headline plus compact labels", "structured callout grid; functional labels require evidence"),
    "problem_solution": ("L3 Problem → Solution Split", "fully inside the brighter solution side, about 48% of canvas height", "top safe zone", "one short phrase per side", "around the divider and product", "problem → product solution → outcome", "contrasting type scale across two regions", "clean split layout, divider rule, opposing texture blocks"),
    "lifestyle_story": ("L4 Lifestyle Story", "in natural use near center-right, visually prominent at 35–45% of frame", "environmental negative space", "one small lifestyle caption", "around the headline and product", "use action → product → headline", "oversized lifestyle headline with small caption", "poster-style crop, asymmetric text, subtle graphic block"),
    "ugc_native": ("L5 UGC Native Static", "in hand or in use near center, recognizable at mobile size", "top safe zone", "one tiny context label", "behind the headline", "real action → product → headline", "direct headline with optional vertical micro-label", "native framing with a thin rule or timestamp-like non-claim index"),
    "review_proof": ("L6 Review / Proof Card", "center-right and primary, 50–60% of canvas height", "upper-left safe zone", "one supplied proof card under 25% of canvas", "between product and proof", "product → supplied proof → headline", "headline plus supplied quote hierarchy", "modular card grid; proof content must be supplied"),
    "offer_value": ("L7 Offer / Value", "large and central, 55–65% of canvas height", "upper safe zone", "one supplied offer chip smaller than product", "around product and offer", "product → offer → optional CTA", "large offer type plus short headline", "poster composition with one offer block; offer must be supplied"),
    "comparison": ("L8 Comparison", "dominant on the preferred side of a clean two-region comparison", "top safe zone", "one supplied-fact label per side", "around divider and labels", "old method → product-led method → benefit", "one short label per side", "split grid and thin divider; comparison claims require evidence"),
    "minimal_editorial": ("L9 Minimal Editorial", "center-lower or right-center, 38–52% of canvas height", "upper negative space", "one small editorial caption", "55–70% of canvas", "headline → product → detail", "oversized sparse type with vertical micro-text", "asymmetric editorial grid, thin rules, generous negative space"),
    "infographic_lite": ("L10 Infographic Lite", "center, 45–55% of canvas height", "upper-center safe zone", "up to two supplied-fact callouts", "between product and labels", "headline → product → supplied facts", "clear headline with numbered 01/02 labels", "structured grid and leader lines; functional callouts require evidence"),
    "poster_editorial": ("L11 Editorial Poster", "off-center and large, 48–62% of canvas height", "oversized type zone behind or beside product", "one small caption", "one open corner", "headline → silhouette → caption", "oversized poster type with strong scale contrast", "graphic shapes, texture block, thin rules, asymmetric crop"),
    "detail_crop": ("L12 Detail Crop", "one product close-up plus one complete product view", "edge-aligned headline zone", "one detail caption", "between crop and full view", "detail → full product → headline", "compact headline with vertical detail label", "split crop, magnified material detail, numbered non-claim marker"),
    "asymmetric_grid": ("L13 Asymmetric Grid", "anchored in one large grid cell, 42–58% of canvas height", "contrasting grid cell", "one small lifestyle caption", "one deliberately empty cell", "headline → product → scene detail", "bold headline plus small editorial caption", "uneven grid, texture blocks, thin rules, non-claim numeric index"),
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

VISUAL_ONLY_HYPOTHESES = [
    ("Premium Product Hero", "clarity", "product_hero", "premium_editorial", "clean studio product hero"),
    ("Minimal Product Clarity", "clarity", "minimal_editorial", "premium_editorial", "refined minimal product study"),
    ("Lifestyle Context", "lifestyle", "poster_editorial", "lifestyle_natural", "believable contextual product use"),
    ("UGC Real Use", "lifestyle", "ugc_native", "ugc_native", "everyday product-in-use snapshot"),
    ("Product Demonstration", "lifestyle", "detail_crop", "lifestyle_natural", "visible handling without performance claims"),
    ("Travel / Everyday Carry", "lifestyle", "asymmetric_grid", "lifestyle_natural", "travel or everyday-carry context"),
    ("Gift Presentation", "gift", "product_hero", "clean_ecommerce", "neutral gift presentation or unboxing"),
    ("Contextual Product Use", "lifestyle", "lifestyle_story", "clean_ecommerce", "product-led everyday context"),
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
        "verified_facts": [],
        "supplied_specs": [],
        "reference_image_visual_facts": [],
        "inferred_context": [],
        "before_after_evidence": [],
        "verified_result_claims": [],
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
        "verified_facts", "supplied_specs", "reference_image_visual_facts",
        "inferred_context", "before_after_evidence", "verified_result_claims",
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


def can_use_offer(data: Dict[str, Any]) -> bool:
    return bool(data["offer_info"].strip())


def can_use_social_proof(data: Dict[str, Any]) -> bool:
    return bool(data["social_proof"].strip())


def can_use_numeric_spec(data: Dict[str, Any]) -> bool:
    return bool(data["supplied_specs"] or any(re.search(r"\d", fact) for fact in data["verified_facts"]))


def can_use_before_after(data: Dict[str, Any]) -> bool:
    return bool(data["before_after_evidence"] or data["verified_result_claims"])


def can_use_comparison_claim(data: Dict[str, Any]) -> bool:
    return bool(data["verified_facts"] or data["key_features"] or data["benefits"] or data["supplied_specs"] or data["verified_result_claims"])


def claim_mode(data: Dict[str, Any]) -> str:
    supplied = (
        data["verified_facts"] or data["key_features"] or data["benefits"] or data["supplied_specs"]
        or data["verified_result_claims"] or data["offer_info"] or data["social_proof"]
        or data["before_after_evidence"]
    )
    return "evidence_backed" if supplied else "visual_only"


def build_claim_safe_fact_pool(data: Dict[str, Any]) -> List[Dict[str, str]]:
    pool: List[Dict[str, str]] = []
    sources = [
        ("verified_facts", data["verified_facts"]),
        ("supplied_features", data["key_features"]),
        ("supplied_benefits", data["benefits"]),
        ("supplied_specs", data["supplied_specs"]),
        ("verified_result_claims", data["verified_result_claims"]),
        ("reference_image_visual_facts", data["reference_image_visual_facts"]),
    ]
    for source, values in sources:
        pool.extend({"text": value.strip(), "source": source} for value in values if value.strip())
    if can_use_offer(data):
        pool.append({"text": data["offer_info"].strip(), "source": "supplied_offer"})
    if can_use_social_proof(data):
        pool.append({"text": data["social_proof"].strip(), "source": "supplied_social_proof"})
    pool.extend({"text": value.strip(), "source": "before_after_evidence"} for value in data["before_after_evidence"] if value.strip())
    return pool


def _claim_fact_pool(data: Dict[str, Any]) -> List[Dict[str, str]]:
    return [fact for fact in build_claim_safe_fact_pool(data) if fact["source"] != "reference_image_visual_facts"]


def category_family(data: Dict[str, Any]) -> str:
    category = data["product_category"].lower()
    if any(alias in category for alias in ("phone case", "mobile accessories", "smartphone accessories", "phone accessories", "iphone case", "magsafe")):
        return "mobile_accessories"
    if any(alias in category for alias in ("skincare", "beauty", "serum", "cosmetic")):
        return "skincare"
    if any(alias in category for alias in ("electronics", "usb-c", "usb c", "hub", "adapter", "charger")):
        return "electronics"
    return "general"


def select_benefit_for_angle(data: Dict[str, Any], angle: Dict[str, str]) -> str:
    benefits = data["benefits"] or data["verified_result_claims"] or data["key_features"] or data["verified_facts"] or data["supplied_specs"]
    if not benefits:
        return ""
    feature_pool = data["key_features"] or data["supplied_specs"] or benefits
    if angle["layout"] == "infographic_lite":
        return feature_pool[0]
    keyword_preferences = {
        "problem": ("protect", "reduce", "less", "fewer", "faster", "clutter", "mess"),
        "lifestyle": ("daily", "easy", "charge", "connect", "light", "comfort", "carry"),
        "benefit": ("more", "even", "hydrate", "connect", "charge", "glow"),
        "comparison": ("reduce", "less", "more", "faster", "easy"),
    }
    for benefit in benefits:
        if any(keyword in benefit.lower() for keyword in keyword_preferences.get(angle["kind"], ())):
            return benefit
    if angle["kind"] == "benefit" and len(benefits) > 1:
        return benefits[1]
    return benefits[0]


def select_audience_for_angle(data: Dict[str, Any], angle: Dict[str, str], benefit: str) -> str:
    audiences = infer_audiences(data)
    family = category_family(data)
    text = f"{data['product_name']} {data['product_category']} {angle['name']} {angle['kind']} {benefit}".lower()
    preferred = None
    if "gift" in text:
        preferred = "tech gift buyers" if family == "electronics" else "gift buyers"
    elif family == "mobile_accessories":
        if angle["kind"] == "problem":
            preferred = "device protection shoppers"
        elif angle["kind"] == "clarity":
            preferred = "minimal accessory buyers"
        elif angle["name"] == "UGC Real Use":
            preferred = "case refresh shoppers"
        elif ("magsafe" in text or "wireless charg" in text or "car mount" in text) and angle["kind"] in {"benefit", "lifestyle", "comparison"}:
            preferred = "MagSafe users"
        elif "protect" in text:
            preferred = "device protection shoppers"
        else:
            preferred = "style-focused phone users"
    elif family == "skincare":
        if angle["kind"] == "clarity":
            preferred = "premium skincare shoppers"
        elif angle["kind"] == "benefit" or any(word in text for word in ("texture", "ingredient", "feature")):
            preferred = "ingredient-aware shoppers"
        elif angle["name"] == "UGC Real Use":
            preferred = "skincare beginners" if data["awareness_stage"] == "cold" else "busy professionals"
        else:
            preferred = "busy professionals"
    elif family == "electronics":
        if "gift" in text:
            preferred = "tech gift buyers"
        elif angle["kind"] in {"problem", "benefit", "comparison"}:
            preferred = "productivity users"
        elif angle["kind"] == "lifestyle" and any(word in text for word in ("travel", "commute", "portable")):
            preferred = "commuters"
        else:
            preferred = "productivity users"
    return preferred if preferred in audiences else audiences[0]


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
    if claim_mode(data) == "visual_only":
        visual_angles = [
            {"name": name, "kind": kind, "layout": layout, "style": style, "scene": scene}
            for name, kind, layout, style, scene in VISUAL_ONLY_HYPOTHESES
        ]
        return [{**angle, "score": score_angle(data, angle)} for angle in visual_angles]
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
        if key not in seen and angle_is_eligible(data, angle):
            unique.append({**angle, "score": score_angle(data, angle)})
            seen.add(key)
    return sorted(unique, key=lambda item: (-item["score"], item["name"]))


def angle_is_eligible(data: Dict[str, Any], angle: Dict[str, str]) -> bool:
    name = angle["name"].lower()
    if angle["kind"] == "offer" and not can_use_offer(data):
        return False
    if angle["kind"] == "proof" and not can_use_social_proof(data):
        return False
    if any(term in name for term in ("before", "after", "transformation")) and not can_use_before_after(data):
        return False
    if angle["kind"] in {"problem", "comparison"} and not can_use_comparison_claim(data):
        return False
    if angle["layout"] == "infographic_lite" and not _claim_fact_pool(data):
        return False
    if angle["kind"] == "benefit" and not _claim_fact_pool(data):
        return False
    return True


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


def lifestyle_headline(data: Dict[str, Any], angle: Dict[str, str], benefit: str, scene: str = "") -> str:
    phrase = benefit_phrase(benefit, data).rstrip(".")
    family = category_family(data)
    if family == "mobile_accessories":
        suffix = "On the Go" if angle.get("name") == "Product Demonstration" else "In Daily Carry"
    elif family == "skincare":
        suffix = "One Simple Step" if angle.get("name") == "Product Demonstration" else "Every Morning"
    elif family == "electronics":
        suffix = "Get More Done" if angle.get("name") == "Product Demonstration" else "In Your Setup"
    else:
        if angle.get("name") == "Product Demonstration":
            suffix = "In Daily Use"
        elif angle.get("name") == "UGC Real Use":
            suffix = "In Your Routine"
        else:
            suffix = "For Your Routine"
    words = f"{phrase}. {suffix}.".split()
    return " ".join(words[:7]).rstrip(".") + "."


def visual_only_copy(data: Dict[str, Any], angle: Dict[str, str], scene: str = "") -> Dict[str, Any]:
    """Generate expressive non-factual copy when claim evidence is absent."""
    family = category_family(data)
    angle_name = angle.get("name")
    family_lines = {
        "mobile_accessories": {
            "Lifestyle Context": "READY FOR EVERYDAY MOVES",
            "UGC Real Use": "OUT THE DOOR",
            "Product Demonstration": "MOVE WITH STYLE",
            "Travel / Everyday Carry": "CITY MODE",
            "Contextual Product Use": "DAILY CARRY MODE",
        },
        "skincare": {
            "Lifestyle Context": "BUILT AROUND YOUR ROUTINE",
            "UGC Real Use": "MORNING MODE",
            "Product Demonstration": "A MOMENT FOR YOU",
            "Travel / Everyday Carry": "CARE ON THE GO",
            "Contextual Product Use": "YOUR DAILY RITUAL",
        },
        "electronics": {
            "Lifestyle Context": "BUILT AROUND YOUR SETUP",
            "UGC Real Use": "DESK MODE",
            "Product Demonstration": "READY WHEN YOU ARE",
            "Travel / Everyday Carry": "WORK MODE, ANYWHERE",
            "Contextual Product Use": "DAILY SETUP ENERGY",
        },
        "general": {
            "Lifestyle Context": "BUILT AROUND YOUR ROUTINE",
            "UGC Real Use": "READY WHEN YOU ARE",
            "Product Demonstration": "IN THE MOMENT",
            "Travel / Everyday Carry": "ON THE GO",
            "Contextual Product Use": "DAILY ESSENTIAL",
        },
    }
    fixed = {
        "Premium Product Hero": "FORM IN FOCUS",
        "Minimal Product Clarity": "PURE FORM",
        "Gift Presentation": "READY TO GIVE",
    }
    headline = fixed.get(angle_name) or family_lines.get(family, family_lines["general"]).get(angle_name, "READY WHEN YOU ARE")
    support_by_angle = {
        "Premium Product Hero": _short_product_name(data["product_name"]),
        "Minimal Product Clarity": "An everyday object study",
        "Lifestyle Context": "Commute / weekend / repeat" if "travel" not in scene.lower() else "Pack / move / repeat",
        "UGC Real Use": "A real-life product moment",
        "Product Demonstration": "Form / detail / movement",
        "Travel / Everyday Carry": "From weekday to weekend",
        "Gift Presentation": "A considered product moment",
        "Contextual Product Use": "Made part of the moment",
    }
    support = support_by_angle.get(angle_name, "")
    return {"headline": headline, "support": support, "callouts": [], "cta": ""}


HARD_CLAIM_PATTERNS = [
    r"\bwaterproof\b", r"\banti[- ]?theft\b", r"\bdrop[- ]?protection\b",
    r"\b\d+(?:\.\d+)?\s*[x×]\s*(?:faster|stronger|better)\b",
    r"\b\d[\d,]*(?:\.\d+)?\s*(?:rpm|w|watts?|db|mah|ml|l|liters?|oz|gb|tb|hours?|%)\b",
    r"\bip\d{2}\b", r"\bmade (?:from|of) [a-z][a-z -]+\b",
    r"\b(?:genuine|full-grain|vegan|recycled|organic) (?:leather|cotton|silicone|aluminum|steel|plastic)\b",
    r"\bcertified\b", r"\bbest[- ]seller\b", r"\bclinically\b",
]


def classify_copy_tier(data: Dict[str, Any], text: str) -> str:
    if not text.strip():
        return "none"
    normalized = _normalized_claim_text(text)
    evidence = [
        variant
        for fact in _claim_fact_pool(data)
        for variant in (_normalized_claim_text(fact["text"]), _normalized_claim_text(benefit_phrase(fact["text"], data)))
    ]
    if any(item and (item in normalized or normalized in item) for item in evidence):
        return "hard_claim"
    if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in HARD_CLAIM_PATTERNS):
        return "hard_claim"
    letters = [char for char in text if char.isalpha()]
    if letters and text == text.upper() and len(text.replace("/", " ").replace(",", " ").split()) <= 5:
        return "creative_lifestyle"
    return "soft_benefit"


def classify_copy(data: Dict[str, Any], copy: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "headline": classify_copy_tier(data, copy["headline"]),
        "support": classify_copy_tier(data, copy["support"]),
        "callouts": [classify_copy_tier(data, item) for item in copy["callouts"]],
        "cta": classify_copy_tier(data, copy["cta"]),
    }


def unsupported_hard_copy_findings(data: Dict[str, Any], copy: Dict[str, Any]) -> List[str]:
    evidence = [
        variant
        for fact in _claim_fact_pool(data)
        for variant in (_normalized_claim_text(fact["text"]), _normalized_claim_text(benefit_phrase(fact["text"], data)))
        if variant
    ]
    findings = []
    texts = [copy["headline"], copy["support"], *copy["callouts"], copy["cta"]]
    for value in texts:
        if classify_copy_tier(data, value) != "hard_claim":
            continue
        normalized = _normalized_claim_text(value)
        if not any(item in normalized or normalized in item for item in evidence):
            findings.append(f"hard claim lacks supplied evidence: {value}")
    return findings


def build_copy(data: Dict[str, Any], angle: Dict[str, str], benefit: str, scene: str = "") -> Dict[str, Any]:
    mode = data["text_overlay_mode"]
    if mode == "none":
        return {"headline": "", "support": "", "callouts": [], "cta": ""}
    if claim_mode(data) == "visual_only":
        return visual_only_copy(data, angle, scene)

    phrase = benefit_phrase(benefit, data)
    layout = angle["layout"]
    clarity_headline = f"Meet {_short_product_name(data['product_name'])}"
    if angle.get("name") == "Minimal Product Clarity":
        clarity_headline = f"{_short_product_name(data['product_name'])} Refined"
    benefit_headline = phrase
    if angle.get("name") == "Benefit / Outcome":
        benefit_headline = " ".join(f"{phrase.rstrip('.')}. Every Day.".split()[:7])
    elif angle.get("name") == "Infographic Feature":
        benefit_headline = " ".join(f"{phrase.rstrip('.')}. At a Glance.".split()[:7])
    problem_headline = phrase
    if angle.get("name") == "Problem → Solution":
        problem_headline = " ".join(f"{phrase.rstrip('.')}. Made Simple.".split()[:7])
    headline = {
        "clarity": clarity_headline,
        "problem": problem_headline,
        "lifestyle": lifestyle_headline(data, angle, benefit, scene),
        "benefit": benefit_headline,
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


def collect_used_claims(data: Dict[str, Any], angle: Dict[str, str], benefit: str, copy: Dict[str, Any]) -> Dict[str, List[str]]:
    if claim_mode(data) == "visual_only":
        sources = ["reference_image_visual_facts"] if data["reference_image_visual_facts"] else ["neutral_copy"]
        return {"used_claims": [], "evidence_source": sources}
    rendered = " ".join([copy["headline"], copy["support"], *copy["callouts"], copy["cta"]]).lower()
    used, sources = [], []
    for fact in build_claim_safe_fact_pool(data):
        variants = {fact["text"].lower(), benefit_phrase(fact["text"], data).lower()}
        if fact["text"] == benefit or any(variant and variant in rendered for variant in variants):
            used.append(fact["text"])
            sources.append(fact["source"])
    if angle["kind"] == "offer" and can_use_offer(data):
        used.append(data["offer_info"])
        sources.append("supplied_offer")
    if angle["kind"] == "proof" and can_use_social_proof(data):
        used.append(data["social_proof"])
        sources.append("supplied_social_proof")
    return {"used_claims": list(dict.fromkeys(used)), "evidence_source": list(dict.fromkeys(sources)) or ["neutral_copy"]}


def build_audience_scene_bridge(data: Dict[str, Any], audience: str, scene: str, benefit: str, index: int) -> Dict[str, Any]:
    moments = ["the moment the product is selected for use", "active product use during a familiar routine", "a contextual product-handling moment", "a recognizable setup moment"]
    if claim_mode(data) == "visual_only":
        behaviors = ["handling the product naturally", "placing the product in a believable routine", "showing the visible product form in context"]
    else:
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


def select_scene_for_hypothesis(data: Dict[str, Any], angle: Dict[str, str], benefit: str, audience: str) -> str:
    text = f"{angle['name']} {angle['kind']} {benefit} {audience}".lower()
    if data["scene_preferences"]:
        terms = set(text.replace("→", " ").replace("/", " ").split())
        ranked_scenes = [(sum(term in scene.lower() for term in terms), scene) for scene in data["scene_preferences"]]
        best_score, best_scene = max(ranked_scenes)
        if best_score > 0:
            return best_scene

    family = category_family(data)
    if family == "mobile_accessories":
        if angle["kind"] == "clarity":
            return "minimal studio or clean desk product hero"
        if "magsafe" in text or "wireless charg" in text:
            return "MagSafe wireless charging or car-mount use"
        if angle["kind"] == "problem" or "protect" in text:
            return "commute protection moment with a believable drop-risk context"
        if angle["name"] == "UGC Real Use":
            return "cafe or everyday-carry phone-in-hand snapshot"
        if angle["kind"] == "lifestyle":
            return "mirror-selfie or cafe everyday-carry moment"
        if "gift" in text:
            return "phone-case gift unboxing"
        return "organized desk with phone and case in practical use"
    if family == "skincare":
        if angle["kind"] == "clarity":
            return "premium studio or refined vanity product hero"
        if angle["kind"] == "benefit" or any(word in text for word in ("texture", "ingredient", "feature")):
            return "close serum texture detail beside a clean vanity"
        if angle["name"] == "UGC Real Use":
            return "natural morning skincare routine in a real bathroom"
        if angle["kind"] == "lifestyle":
            return "simple morning vanity routine with product in use"
        if "gift" in text:
            return "skincare gift unboxing on a clean vanity"
        return "clean vanity problem-to-routine transition"
    if family == "electronics":
        if angle["kind"] == "clarity":
            return "clean studio or minimal desk product hero"
        if angle["kind"] == "problem":
            return "cable-clutter desk transitioning to an organized hub setup"
        if angle["kind"] == "lifestyle":
            return "real laptop connection and multi-port use at a desk or while traveling"
        if "gift" in text:
            return "tech gift unboxing beside a laptop setup"
        return "organized productivity desk with visible connected accessories"
    if "gift" in text:
        return "believable gift unboxing moment"
    if angle["kind"] == "clarity":
        return angle["scene"]
    return f"believable product-use environment; {angle['scene']}"


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
    visible = ""
    if data["reference_image_visual_facts"] and not data["product_identity_constraints"]:
        visible = " Visible reference facts only: " + ", ".join(data["reference_image_visual_facts"]) + "."
    if data["reference_image"]:
        return f"Preserve the supplied product reference exactly—lock {locked}. Do not redesign the SKU.{visible}"
    return f"Preserve the described product identity—keep {locked} consistent. Do not invent a different SKU or packaging.{visible}"


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
    parts.append(f"use {data['language']} only; legible contrast; safe margins; no extra copy")
    return "; ".join(parts) + "."


def universal_prompt(data: Dict[str, Any], plan: Dict[str, Any]) -> str:
    layout = plan["layout_profile"]
    dna = plan["visual_dna"]
    negatives = plan["negative_constraints"]
    return "\n\n".join([
        f"Create a {data['aspect_ratio']} Meta ecommerce ad image for {data['placement'].replace('_', ' ')}.",
        f"PRODUCT: {product_identity_instruction(data)}",
        f"SCENE: {plan['scene']}; {plan['audience_scene_bridge']['visible_behavior']}. Props stay relevant and secondary.",
        f"PLACEMENT: {plan['placement_instruction']}",
        f"COMPOSITION: Product {layout['product_position']}; headline {layout['headline_zone']}; support {layout['support_zone']}; keep {layout['negative_space']} uncluttered; flow {layout['visual_flow']}.",
        f"DESIGN: {layout['typography']}; {layout['graphic_structure']}.",
        f"LOOK: {dna['lighting']}. {dna['camera_language']}. {dna['background_character']}. {dna['color_mood']}. {dna['material_treatment']}. {dna['graphic_treatment']}.",
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


def _normalized_claim_text(value: str) -> str:
    return re.sub(r"[^a-z0-9%×]+", " ", value.lower().replace(",", "")).strip()


def unsupported_claim_findings(data: Dict[str, Any], prompt: str) -> List[str]:
    positive_prompt = prompt.split("AVOID:", 1)[0]
    normalized_prompt = _normalized_claim_text(positive_prompt)
    evidence = " ".join(fact["text"] for fact in _claim_fact_pool(data))
    if can_use_offer(data):
        evidence += " " + data["offer_info"]
    if can_use_social_proof(data):
        evidence += " " + data["social_proof"]
    normalized_evidence = _normalized_claim_text(evidence)
    findings = []

    numeric_patterns = [
        r"\b\d[\d,]*(?:\.\d+)?\s*(?:rpm|w|watt|watts|db|hours?|%)\b",
        r"\b\d+(?:\.\d+)?\s*[x×]\s*(?:faster|stronger|better)\b",
    ]
    for pattern in numeric_patterns:
        for match in re.findall(pattern, positive_prompt, flags=re.IGNORECASE):
            if _normalized_claim_text(match) not in normalized_evidence:
                findings.append(f"numeric claim lacks supplied source: {match}")

    risky_phrases = [
        "faster", "quiet motor", "lower noise", "temperature control", "smart temperature",
        "heat damage", "battery life", "all hair types", "salon results", "clinically",
        "waterproof", "drop-proof", "drop protection", "anti-theft", "anti theft",
        "anti-yellowing", "certified", "guarantee",
        "free shipping", "limited time", "best seller", "award winning", "rated",
    ]
    for phrase in risky_phrases:
        if phrase in normalized_prompt and phrase not in normalized_evidence:
            findings.append(f"unsupported claim phrase: {phrase}")
    if ("before" in normalized_prompt or "after" in normalized_prompt) and not can_use_before_after(data):
        findings.append("before/after language lacks explicit evidence")
    if any(symbol in positive_prompt for symbol in ("★", "⭐")) and not can_use_social_proof(data):
        findings.append("rating symbol lacks supplied social proof")
    return list(dict.fromkeys(findings))


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
    if any(term in plan["angle"]["name"].lower() for term in ("before", "after", "transformation")) and not can_use_before_after(data):
        findings.append("before/after angle lacks explicit evidence")
    if plan["angle_kind"] in {"problem", "comparison"} and not can_use_comparison_claim(data):
        findings.append("comparison angle lacks supplied product facts")
    findings.extend(unsupported_hard_copy_findings(data, plan["copy"]))
    if plan["placement_instruction"] not in prompt:
        findings.append("placement safe-zone instruction missing from render prompt")
    if data["text_overlay_mode"] != "none" and not headline_is_natural(plan["copy"]["headline"], plan["angle_kind"]):
        findings.append("headline is empty, too long, or resembles broken template grammar")
    expected_audience = select_audience_for_angle(data, plan["angle"], plan["benefit"])
    if plan["audience"] != expected_audience:
        findings.append("audience is not compatible with angle, category, and benefit")
    expected_scene = select_scene_for_hypothesis(data, plan["angle"], plan["benefit"], plan["audience"])
    if plan["scene"] != expected_scene:
        findings.append("scene is not compatible with the selected hypothesis")
    findings.extend(unsupported_claim_findings(data, prompt))
    return {
        "pass": not findings,
        "findings": findings,
        "revised": False,
        "prompt_word_count": word_count,
        "checks": ["product fidelity", "one-glance message", "product prominence", "layout clarity", "copy tier classification", "hard claim evidence", "creative copy freedom", "placement safe-zone compiled", "unsupported claim check", "numeric claim source check", "before/after evidence check", "proof source check", "offer source check", "spec source check", "compatibility claim check", "headline grammar", "audience-angle compatibility", "scene-angle compatibility", "prompt word budget"],
    }


def build_creatives(data: Dict[str, Any]) -> Dict[str, Any]:
    angles = select_angles(data, data["generation_count"])
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
        benefit = select_benefit_for_angle(data, angle)
        audience = select_audience_for_angle(data, angle, benefit)
        scene = select_scene_for_hypothesis(data, angle, benefit, audience)
        layout_values = LAYOUT_PROFILES[angle["layout"]]
        layout = dict(zip(["name", "product_position", "headline_zone", "support_zone", "negative_space", "visual_flow", "typography", "graphic_structure"], layout_values))
        selected_style = select_visual_style(data, angle, index)
        dna_values = VISUAL_DNA[selected_style]
        dna = dict(zip(["name", "lighting", "camera_language", "background_character", "color_mood", "material_treatment", "graphic_treatment"], dna_values))
        bridge = build_audience_scene_bridge(data, audience, scene, benefit, index)
        copy = build_copy(data, angle, benefit, scene)
        copy_tiers = classify_copy(data, copy)
        evidence = collect_used_claims(data, angle, benefit, copy)
        plan = {
            "angle_kind": angle["kind"],
            "angle": angle,
            "benefit": benefit,
            "audience": audience,
            "scene": scene,
            "audience_scene_bridge": bridge,
            "layout_profile": layout,
            "visual_dna": dna,
            "copy": copy,
            "copy_tiers": copy_tiers,
            "used_claims": evidence["used_claims"],
            "evidence_source": evidence["evidence_source"],
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
                "rationale": (
                    f"Express {benefit} through a {angle['name']} concept for {audience}."
                    if benefit else f"Present the visible product safely through a {angle['name']} concept for {audience}."
                ),
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
                "typography": layout["typography"], "graphic_structure": layout["graphic_structure"],
                "text_mode": data["text_overlay_mode"], "copy": plan["copy"], "copy_tiers": copy_tiers,
            },
            "render_prompt": prompt,
            "model_prompts": {
                "universal": prompt,
                "gpt_image_2": prompt + "\n\nRender the exact requested typography with precise alignment and no added text.",
                "nano_banana": prompt + "\n\nPrioritize product fidelity and composition; keep typography simple and exact.",
            },
            "negative_constraints": negatives,
            "evidence_lock": {
                "claim_mode": claim_mode(data),
                "used_claims": evidence["used_claims"],
                "evidence_source": evidence["evidence_source"],
                "copy_tiers": copy_tiers,
            },
            "quality_check": quality,
        })

    angle_count = len({item["hypothesis"]["angle"] for item in creatives})
    layout_count = len({item["visual_plan"]["layout"] for item in creatives})
    combo_count = len({(item["hypothesis"]["angle"], item["visual_plan"]["scene"], item["visual_plan"]["layout"]) for item in creatives})
    headlines = [item["visual_plan"]["copy"]["headline"] for item in creatives if item["visual_plan"]["copy"]["headline"]]
    headline_count = len(set(headlines))
    findings = []
    required_angles = min(len(creatives), {"low": 2, "medium": 3, "high": 4}[data["variation_strength"]])
    required_layouts = min(len(creatives), {"low": 1, "medium": 2, "high": 3}[data["variation_strength"]])
    if angle_count < required_angles:
        findings.append(f"angle diversity below required minimum ({angle_count}/{required_angles})")
    if layout_count < required_layouts:
        findings.append(f"layout diversity below required minimum ({layout_count}/{required_layouts})")
    if data["variation_strength"] == "high" and combo_count != len(creatives):
        findings.append("duplicate angle-scene-layout hypotheses detected")
    if data["variation_strength"] == "high" and data["text_overlay_mode"] != "none":
        required_headlines = min(len(creatives), 6 if len(creatives) >= 8 else max(1, (len(creatives) * 3 + 3) // 4))
        if headline_count < required_headlines:
            findings.append(f"headline diversity below required minimum ({headline_count}/{required_headlines})")
    hypothesis_audiences: Dict[Any, set] = {}
    for item in creatives:
        key = (item["hypothesis"]["angle"], item["hypothesis"]["core_benefit"], item["visual_plan"]["scene"])
        hypothesis_audiences.setdefault(key, set()).add(item["hypothesis"]["audience"])
    if data["variation_strength"] == "high" and any(len(values) > 1 for values in hypothesis_audiences.values()):
        findings.append("mechanical audience swapping detected for an unchanged hypothesis")
    return {
        "schema_version": "2.0",
        "input_summary": {
            "product_name": data["product_name"], "product_category": data["product_category"],
            "generation_count": data["generation_count"], "placement": data["placement"],
            "aspect_ratio": data["aspect_ratio"], "variation_strength": data["variation_strength"],
            "claim_mode": claim_mode(data),
        },
        "creative_plans": creatives,
        "quality_checks": {
            "pass": not findings and all(item["quality_check"]["pass"] for item in creatives),
            "findings": findings, "distinct_angles": angle_count, "distinct_layouts": layout_count,
            "distinct_hypothesis_combinations": combo_count, "distinct_headlines": headline_count,
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
