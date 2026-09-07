import importlib.util
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / ".claude"
    / "skills"
    / "facebook-ad-creative"
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
    combos = {
        (
            item["creative_plan"]["scene"],
            item["creative_plan"]["style"],
            item["creative_plan"]["layout"],
        )
        for item in creatives
    }

    assert len(creatives) == 4
    assert len(combos) == 4
    assert all("gpt_image_2" in item["model_prompts"] for item in creatives)
    assert all("nano_banana" in item["model_prompts"] for item in creatives)
    assert all("This variation focuses on" in item["creative_plan"]["difference_statement"] for item in creatives)


def test_missing_required_fields_raise_error():
    try:
        compile_creatives.normalize({"product_name": "Only Name"})
    except ValueError as exc:
        assert "product_category" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing fields")


def test_text_mode_compiles_required_typography_contract():
    data = compile_creatives.normalize({"product_name":"Bag","product_category":"apparel","product_description":"A compact everyday bag.","language":"en","text_overlay_mode":"standard"})
    prompt = compile_creatives.build_creatives(data)["creative_plans"][0]["model_prompts"]["universal"]
    assert "Rendering the supplied copy is required" in prompt
    assert "Target copy language: en" in prompt
    assert "Do not invent extra copy" in prompt


def test_none_mode_prohibits_all_rendered_text():
    data = compile_creatives.normalize({"product_name":"Bag","product_category":"apparel","product_description":"A compact everyday bag.","text_overlay_mode":"none"})
    creative = compile_creatives.build_creatives(data)["creative_plans"][0]
    assert creative["creative_plan"]["copy"] == {"headline":"","subheadline":"","bullets":[],"cta":""}
    assert "Render no words, letters" in creative["model_prompts"]["universal"]
