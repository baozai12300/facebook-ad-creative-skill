import importlib.util
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "compile_creatives.py"
)


spec = importlib.util.spec_from_file_location("compile_creatives", SCRIPT_PATH)
compile_creatives = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(compile_creatives)


def test_builds_requested_number_of_distinct_creatives():
    data = compile_creatives.normalize(
        {
            "product_name": "Test Product",
            "product_category": "kitchen",
            "product_description": "A useful product for daily cooking.",
            "key_features": ["easy clean", "compact"],
            "benefits": ["faster meal prep", "less mess"],
            "generation_count": 4,
            "variation_strength": "high",
        }
    )

    output = compile_creatives.build_creatives(data)
    creatives = output["creative_plans"]
    combos = {(item["hypothesis"]["angle"], item["visual_plan"]["scene"], item["visual_plan"]["layout"]) for item in creatives}

    assert len(creatives) == 4
    assert len(combos) == 4
    assert all("gpt_image_2" in item["model_prompts"] for item in creatives)
    assert all("nano_banana" in item["model_prompts"] for item in creatives)
    assert output["schema_version"] == "2.0"
    assert output["quality_checks"]["pass"] is True
    assert len({item["hypothesis"]["angle"] for item in creatives}) == 4


def test_missing_required_fields_raise_error():
    try:
        compile_creatives.normalize({"product_name": "Only Name"})
    except ValueError as exc:
        assert "product_category" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing fields")


def test_text_mode_compiles_required_typography_contract():
    data = compile_creatives.normalize({"product_name":"Bag","product_category":"apparel","product_description":"A compact everyday bag.","language":"en","text_overlay_mode":"standard"})
    creative = compile_creatives.build_creatives(data)["creative_plans"][0]
    prompt = creative["render_prompt"]
    assert "Render headline exactly" in prompt
    assert "use en only" in prompt
    assert "no extra copy" in prompt
    assert creative["visual_plan"]["headline_zone"] in prompt


def test_none_mode_prohibits_all_rendered_text():
    data = compile_creatives.normalize({"product_name":"Bag","product_category":"apparel","product_description":"A compact everyday bag.","text_overlay_mode":"none"})
    creative = compile_creatives.build_creatives(data)["creative_plans"][0]
    assert creative["visual_plan"]["copy"] == {"headline":"","support":"","callouts":[],"cta":""}
    assert "No rendered words, letters" in creative["render_prompt"]


def test_audience_is_fused_into_scene_and_prompt():
    data = compile_creatives.normalize({"product_name":"Travel Bag","product_category":"apparel","product_description":"A compact bag for daily carry.","target_audiences":["urban commuters"],"benefits":["hands-free organization"]})
    creative = compile_creatives.build_creatives(data)["creative_plans"][0]
    bridge = creative["visual_plan"]["audience_scene_bridge"]
    prompt = creative["render_prompt"]
    assert bridge["use_moment"] and bridge["visible_behavior"] and bridge["camera_language"]
    assert bridge["visible_behavior"] in prompt
    assert "Target audience" not in prompt
    assert "Interest cues" not in prompt
    assert "rationale" not in prompt.lower()


def test_render_prompt_is_compact_and_keeps_strategy_internal():
    data = compile_creatives.normalize({"product_name":"Serum","product_category":"beauty skincare","product_description":"A lightweight daily serum.","benefits":["hydrated finish"],"target_audiences":["busy professionals"],"interests":["skincare routine"],"generation_count":4})
    output = compile_creatives.build_creatives(data)
    for creative in output["creative_plans"]:
        prompt = creative["render_prompt"]
        assert len(prompt.split()) <= 240
        assert "PRODUCT:" in prompt and "COMPOSITION:" in prompt and "AVOID:" in prompt
        assert creative["hypothesis"]["audience"] not in prompt
        assert creative["quality_check"]["pass"] is True


def test_offer_and_proof_angles_require_supplied_evidence():
    base = {"product_name":"Bag","product_category":"apparel","product_description":"A compact everyday bag."}
    without_evidence = compile_creatives.choose_angles(compile_creatives.normalize(base))
    assert all(item["kind"] not in {"offer", "proof"} for item in without_evidence)
    with_evidence = compile_creatives.choose_angles(compile_creatives.normalize({**base,"offer_info":"20% off this week","social_proof":"Verified buyer quote"}))
    assert {item["kind"] for item in with_evidence} >= {"offer", "proof"}
    batch = compile_creatives.build_creatives(compile_creatives.normalize({**base,"offer_info":"20% off this week","generation_count":8}))
    assert "Supplied Offer / Value" in {item["hypothesis"]["angle"] for item in batch["creative_plans"]}


def test_invalid_enums_and_generation_count_are_rejected():
    base = {"product_name":"Bag","product_category":"apparel","product_description":"A compact everyday bag."}
    for update in ({"placement":"unknown"},{"generation_count":25},{"generation_count":"4"}):
        try:
            compile_creatives.normalize({**base, **update})
        except ValueError:
            pass
        else:
            raise AssertionError(f"Expected validation error for {update}")


def test_story_defaults_to_vertical_placement_geometry():
    data = compile_creatives.normalize({"product_name":"Bag","product_category":"apparel","product_description":"A compact everyday bag.","placement":"story"})
    creative = compile_creatives.build_creatives(data)["creative_plans"][0]
    assert data["aspect_ratio"] == "9:16"
    assert creative["placement_plan"]["canvas"] == "1080x1920"
    assert "top and bottom" in creative["placement_plan"]["adaptation_notes"]
