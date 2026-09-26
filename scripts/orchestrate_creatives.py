#!/usr/bin/env python3
"""Provider-agnostic orchestration for product analysis and ad previews.

This module does not bind a vision or image-generation vendor. Applications
inject configured providers; the Creative Skill consumes ProductAnalysis and
returns reviewable preview plans before any image generation is requested.
"""

from __future__ import annotations

import copy
from typing import Any, Callable, Dict, List, Optional

from compile_creatives import build_creatives, normalize as normalize_creative_input


UNKNOWN = "unknown"
MAX_PRODUCT_IMAGES = 8


def _strings(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(str(item).strip() for item in value if str(item).strip()))


def _text(value: Any, default: str = UNKNOWN) -> str:
    text = str(value).strip() if value is not None else ""
    return text or default


def normalize_product_analysis(raw: Dict[str, Any], user_product_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Normalize a provider result into the vendor-neutral ProductAnalysis contract."""
    if not isinstance(raw, dict):
        raise ValueError("Vision result must be an object")
    user = user_product_info or {}
    visual = raw.get("visual_identity") if isinstance(raw.get("visual_identity"), dict) else {}
    category = _text(user.get("product_category"), "") or _text(raw.get("product_category"))
    name = _text(user.get("product_name"), "") or _text(raw.get("product_name"))
    supplied = _strings(user.get("user_supplied_facts", user.get("verified_facts", [])))
    provider_supplied = _strings(raw.get("user_supplied_facts"))
    inferred = _strings(raw.get("inferred_context", raw.get("possible_use_contexts", [])))
    scenes = _strings(raw.get("possible_use_scenes", raw.get("possible_use_contexts", inferred)))
    confidence = raw.get("confidence") if isinstance(raw.get("confidence"), dict) else {}
    normalized_confidence = {
        str(key): float(value)
        for key, value in confidence.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 1
    }
    return {
        "analysis_version": "1.0",
        "product_category": category,
        "product_name": name,
        "visual_identity": {
            "shape": _text(visual.get("shape")),
            "proportions": _text(visual.get("proportions")),
            "colors": _strings(visual.get("colors", visual.get("primary_colors", []))),
            "materials": _strings(visual.get("materials", visual.get("materials_visible", []))),
            "finish": _text(visual.get("finish")),
            "distinctive_details": _strings(visual.get("distinctive_details", visual.get("distinctive_parts", []))),
            "controls": _strings(visual.get("controls", visual.get("control_elements", []))),
            "logo": _text(visual.get("logo", visual.get("visible_logo"))),
            "visible_text": _strings(visual.get("visible_text")),
        },
        "visible_facts": _strings(raw.get("visible_facts")),
        "user_supplied_facts": list(dict.fromkeys(supplied + provider_supplied)),
        "inferred_context": inferred,
        "unknowns": _strings(raw.get("unknowns", raw.get("unknown", []))),
        "protected_identity": _strings(raw.get("protected_identity")),
        "possible_use_scenes": scenes,
        "confidence": normalized_confidence,
        "conflicts": list(raw.get("conflicts", [])) if isinstance(raw.get("conflicts"), list) else [],
        "source": {
            "provider": _text(raw.get("provider"), "unspecified"),
            "model": _text(raw.get("model"), "unspecified"),
        },
    }


class VisionAdapter:
    """Normalize arbitrary provider output through an optional injected mapper."""

    def __init__(self, mapper: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None):
        self.mapper = mapper

    def normalize(self, raw: Dict[str, Any], user_product_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        mapped = self.mapper(raw) if self.mapper else raw
        return normalize_product_analysis(mapped, user_product_info)


def analyze_product(
    images: List[str],
    model: str,
    provider: Any,
    user_product_info: Optional[Dict[str, Any]] = None,
    adapter: Optional[VisionAdapter] = None,
) -> Dict[str, Any]:
    """Call any injected multimodal provider and return normalized ProductAnalysis."""
    if not isinstance(images, list) or not 1 <= len(images) <= MAX_PRODUCT_IMAGES:
        raise ValueError("images must contain 1 to 8 product image references")
    if not hasattr(provider, "analyze_product"):
        raise TypeError("provider must implement analyze_product(images, model, user_product_info)")
    raw = provider.analyze_product(images=images, model=model, user_product_info=user_product_info or {})
    normalizer = adapter or VisionAdapter(getattr(provider, "normalize_product_analysis", None))
    analysis = normalizer.normalize(raw, user_product_info)
    analysis["source"] = {"provider": getattr(provider, "name", provider.__class__.__name__), "model": model}
    return analysis


def _compiler_input(product_analysis: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
    analysis = normalize_product_analysis(product_analysis, settings)
    description = settings.get("product_description") or "Normalized product analysis supplied by the application."
    payload = {
        **settings,
        "product_name": analysis["product_name"],
        "product_category": analysis["product_category"],
        "product_description": description,
        "verified_facts": list(dict.fromkeys(_strings(settings.get("verified_facts")) + analysis["user_supplied_facts"])),
        "reference_image_visual_facts": analysis["visible_facts"],
        "inferred_context": analysis["inferred_context"],
        "product_identity_constraints": analysis["protected_identity"],
        "scene_preferences": _strings(settings.get("scene_preferences")) or analysis["possible_use_scenes"],
    }
    return normalize_creative_input(payload)


def create_creative_preview_plans(product_analysis: Dict[str, Any], campaign_settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run the Creative Skill and return plans for frontend review, not image output."""
    compiled = build_creatives(_compiler_input(product_analysis, campaign_settings))
    previews = []
    for item in compiled["creative_plans"]:
        hypothesis = item["hypothesis"]
        visual = item["visual_plan"]
        copy_plan = visual["copy"]
        placement = item["placement_plan"]
        previews.append({
            "creative_id": item["creative_id"],
            "title": hypothesis["angle"],
            "status": "draft",
            "strategy": {
                "audience": hypothesis["audience"],
                "angle": hypothesis["angle"],
                "message": hypothesis["core_benefit"] or copy_plan["headline"],
            },
            "visual": {
                "scene": visual["scene"],
                "product_action": visual["audience_scene_bridge"]["visible_behavior"],
                "layout": visual["layout"],
                "camera": visual["visual_dna"]["camera_language"],
                "lighting": visual["visual_dna"]["lighting"],
                "visual_dna": visual["visual_dna"]["name"],
                "typography": visual.get("typography", ""),
                "graphic_structure": visual.get("graphic_structure_details", visual.get("graphic_structure", "")),
                "typography_structure": visual.get("typography_structure", {}),
                "structural_signature": visual.get("structural_signature", ""),
                "composition_geometry": visual.get("composition_geometry", ""),
            },
            "copy": {
                "headline": copy_plan["headline"],
                "support": copy_plan["support"],
                "support_line": visual.get("typography_structure", {}).get("support_line", ""),
                "micro_label": visual.get("typography_structure", {}).get("micro_label", ""),
                "caption": visual.get("typography_structure", {}).get("caption", ""),
                "index_label": visual.get("typography_structure", {}).get("index_label", ""),
            },
            "placement": {
                "platform": campaign_settings.get("platform", "meta").title(),
                "placement": placement["placement"].replace("_", " ").title(),
                "ratio": placement["aspect_ratio"],
            },
            "evidence": {
                "claims_used": item["evidence_lock"]["used_claims"],
                "sources": item["evidence_lock"]["evidence_source"],
                "copy_tiers": item["evidence_lock"].get("copy_tiers", {}),
            },
            "render_prompt": item["render_prompt"],
            "quality": item["quality_check"],
            "typography_salience_check": item["quality_check"].get("typography_salience_check", {}),
            "quality_pass": item["quality_check"]["pass"],
            "layout_intelligence": item.get("layout_intelligence", {"used": False, "strength": "none", "match_level": "", "sample_count": 0, "selected_layout_family": "", "selected_composition_type": "", "selected_reference_pattern": ""}),
        })
    return previews


def approve_preview_plans(
    preview_plans: List[Dict[str, Any]],
    selected_ids: List[str],
    edits: Optional[Dict[str, Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Apply frontend edits and mark only selected plans as approved."""
    selected = set(selected_ids)
    known = {plan["creative_id"] for plan in preview_plans}
    missing = selected - known
    if missing:
        raise ValueError("Unknown creative ids: " + ", ".join(sorted(missing)))
    approved = []
    for original in preview_plans:
        if original["creative_id"] not in selected:
            continue
        plan = copy.deepcopy(original)
        patch = (edits or {}).get(plan["creative_id"], {})
        for section in ("strategy", "visual", "copy", "placement"):
            if isinstance(patch.get(section), dict):
                plan[section].update(patch[section])
        if "render_prompt" in patch:
            plan["render_prompt"] = _text(patch["render_prompt"], "")
        plan["status"] = "approved"
        approved.append(plan)
    return approved


def build_render_payloads(
    product_images: List[str],
    approved_plans: List[Dict[str, Any]],
    image_model: str,
    provider: str,
) -> List[Dict[str, Any]]:
    """Create provider-neutral payloads; this function never calls an image model."""
    if not isinstance(product_images, list) or not 1 <= len(product_images) <= MAX_PRODUCT_IMAGES:
        raise ValueError("product_images must contain 1 to 8 image references")
    payloads = []
    for plan in approved_plans:
        if plan.get("status") != "approved":
            raise ValueError(f"Creative {plan.get('creative_id', '?')} is not approved")
        payloads.append({
            "creative_id": plan["creative_id"],
            "provider": provider,
            "model": image_model,
            "product_images": product_images,
            "render_prompt": plan["render_prompt"],
            "placement": plan["placement"],
            "evidence": plan["evidence"],
        })
    return payloads


def generate_ad_image(
    product_images: List[str], approved_creative_plan: Dict[str, Any], image_model: str, provider: Any
) -> Any:
    """Optional application boundary; call only after explicit approval."""
    payload = build_render_payloads(product_images, [approved_creative_plan], image_model, getattr(provider, "name", provider.__class__.__name__))[0]
    if not hasattr(provider, "generate_ad_image"):
        raise TypeError("provider must implement generate_ad_image(payload)")
    return provider.generate_ad_image(payload)
