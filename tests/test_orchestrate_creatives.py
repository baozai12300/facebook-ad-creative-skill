import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SCRIPT_PATH = ROOT / "scripts" / "orchestrate_creatives.py"
spec = importlib.util.spec_from_file_location("orchestrate_creatives", SCRIPT_PATH)
orchestration = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(orchestration)


HAIR_DRYER_RAW = {
    "product_category": "hair dryer",
    "product_name": "Compact Hair Dryer",
    "visual_identity": {
        "shape": "handheld T-shaped form with cylindrical barrel",
        "proportions": "straight handle shorter than barrel",
        "primary_colors": ["gunmetal gray", "black", "cyan"],
        "materials_visible": ["metallic-look shell", "glossy dark plastic"],
        "finish": "satin gunmetal",
        "distinctive_parts": ["circular turbine-style front grille", "chrome outer grille ring", "glossy dark lower cap"],
        "control_elements": ["vertical black control panel", "two circular buttons"],
        "visible_logo": "unknown",
        "visible_text": [],
    },
    "visible_facts": ["gunmetal-gray body", "circular front grille", "cyan display above two buttons"],
    "inferred_context": ["personal grooming routine"],
    "unknowns": ["motor speed", "wattage", "noise level", "temperature behavior"],
    "protected_identity": [
        "gunmetal-gray cylindrical body", "circular turbine-style front grille",
        "chrome outer grille ring", "vertical black control panel",
        "cyan display above two circular buttons", "straight handle proportions",
        "glossy dark lower cap",
    ],
    "possible_use_scenes": ["bathroom vanity product handling", "travel packing context"],
    "confidence": {"category": 0.97, "identity": 0.94},
}


class FakeVisionProvider:
    name = "configured-vision-provider"

    def analyze_product(self, images, model, user_product_info):
        assert len(images) == 2
        result = dict(HAIR_DRYER_RAW)
        result["provider"] = self.name
        result["model"] = model
        return result


def test_vision_provider_is_injected_and_normalized():
    result = orchestration.analyze_product(
        ["front.png", "side.png"], "vision-model-from-config", FakeVisionProvider(),
        {"product_name": "User Named Dryer", "user_supplied_facts": ["folding travel pouch included"]},
    )
    assert result["product_name"] == "User Named Dryer"
    assert result["visual_identity"]["colors"] == ["gunmetal gray", "black", "cyan"]
    assert result["user_supplied_facts"] == ["folding travel pouch included"]
    assert result["source"] == {"provider": "configured-vision-provider", "model": "vision-model-from-config"}


def test_product_analysis_separates_visible_inferred_and_unknown():
    result = orchestration.normalize_product_analysis(HAIR_DRYER_RAW)
    assert "gunmetal-gray body" in result["visible_facts"]
    assert "personal grooming routine" in result["inferred_context"]
    assert "wattage" in result["unknowns"]
    assert "wattage" not in result["visible_facts"]


def test_creative_skill_returns_eight_draft_preview_plans():
    analysis = orchestration.normalize_product_analysis(HAIR_DRYER_RAW)
    plans = orchestration.create_creative_preview_plans(analysis, {"generation_count": 8, "placement": "feed", "variation_strength": "high"})
    assert len(plans) == 8
    assert all(plan["status"] == "draft" for plan in plans)
    assert all(plan["quality"]["pass"] is True for plan in plans)
    assert all("render_prompt" in plan for plan in plans)
    assert all("gunmetal-gray cylindrical body" in plan["render_prompt"] for plan in plans)
    assert all(plan["evidence"]["claims_used"] == [] for plan in plans)


def test_only_selected_approved_plans_become_render_payloads():
    analysis = orchestration.normalize_product_analysis(HAIR_DRYER_RAW)
    plans = orchestration.create_creative_preview_plans(analysis, {"generation_count": 8})
    approved = orchestration.approve_preview_plans(plans, ["C01", "C04", "C06"])
    payloads = orchestration.build_render_payloads(["front.png", "side.png"], approved, "configured-image-model", "configured-image-provider")
    assert [item["creative_id"] for item in payloads] == ["C01", "C04", "C06"]
    assert all(item["provider"] == "configured-image-provider" for item in payloads)
    assert all(item["model"] == "configured-image-model" for item in payloads)
    assert all("image" not in item for item in payloads)


def test_draft_plan_cannot_cross_generation_boundary():
    analysis = orchestration.normalize_product_analysis(HAIR_DRYER_RAW)
    draft = orchestration.create_creative_preview_plans(analysis, {"generation_count": 1})[0]
    try:
        orchestration.build_render_payloads(["front.png"], [draft], "model", "provider")
    except ValueError as exc:
        assert "not approved" in str(exc)
    else:
        raise AssertionError("Expected draft plan to be rejected")


def test_image_input_is_limited_to_eight():
    try:
        orchestration.analyze_product([f"{index}.png" for index in range(9)], "model", FakeVisionProvider())
    except ValueError as exc:
        assert "1 to 8" in str(exc)
    else:
        raise AssertionError("Expected image limit validation")
