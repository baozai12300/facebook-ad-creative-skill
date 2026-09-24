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


def test_phone_case_uses_specific_audiences_and_real_scenes():
    data = compile_creatives.normalize({"product_name":"MagSafe Clear Case","product_category":"phone case","product_description":"A slim protective phone case.","benefits":["everyday device protection"],"generation_count":8})
    output = compile_creatives.build_creatives(data)
    audiences = {item["hypothesis"]["audience"] for item in output["creative_plans"]}
    scenes = " ".join(item["visual_plan"]["scene"] for item in output["creative_plans"])
    assert "device protection shoppers" in audiences
    assert "MagSafe users" in audiences
    assert any(cue in scenes for cue in ("commute", "desk", "mirror selfie", "wireless charging"))
    assert "broad ecommerce shoppers" not in audiences


def test_usb_c_hub_copy_is_short_and_natural():
    base = {"product_name":"USB-C Hub","product_category":"electronics","product_description":"A compact multi-port desk hub."}
    assert compile_creatives.benefit_phrase("reduce cable switching", base) == "Fewer Cable Swaps"
    assert compile_creatives.benefit_phrase("connect more desk accessories", base) == "More Ports. One Hub."
    data = compile_creatives.normalize({**base,"benefits":["reduce cable switching","connect more desk accessories"],"generation_count":8})
    output = compile_creatives.build_creatives(data)
    for item in output["creative_plans"]:
        headline = item["visual_plan"]["copy"]["headline"]
        assert "A simpler way to get" not in headline
        assert "Make connect" not in headline
        assert item["quality_check"]["pass"] is True


def test_all_placement_safe_zones_are_compiled_into_prompt():
    expected = {
        "feed": ("center 80%", "do not place key elements against an edge"),
        "story": ("middle 70%", "top and bottom interface zones"),
        "reels": ("upper-middle", "bottom region visually quiet"),
        "carousel": ("native 1:1", "never crop a Feed version"),
    }
    for placement, phrases in expected.items():
        data = compile_creatives.normalize({"product_name":"Case","product_category":"phone case","product_description":"A slim protective case.","placement":placement})
        creative = compile_creatives.build_creatives(data)["creative_plans"][0]
        assert all(phrase in creative["render_prompt"] for phrase in phrases)
        assert creative["quality_check"]["pass"] is True


def test_awareness_stage_changes_ranked_angle_priorities():
    base = {"product_name":"USB-C Hub","product_category":"electronics","product_description":"A compact desk hub.","benefits":["reduce cable switching"],"social_proof":"A supplied verified buyer quote","offer_info":"Save 10%"}
    cold = [item["name"] for item in compile_creatives.choose_angles(compile_creatives.normalize({**base,"awareness_stage":"cold"}))[:5]]
    warm = [item["name"] for item in compile_creatives.choose_angles(compile_creatives.normalize({**base,"awareness_stage":"warm"}))[:5]]
    hot = [item["name"] for item in compile_creatives.choose_angles(compile_creatives.normalize({**base,"awareness_stage":"hot"}))[:5]]
    assert "Problem → Solution" in cold and "Product Demonstration" in cold
    assert warm[0] == "Supplied Social Proof" and "Objection Handling" in warm
    assert hot[0] == "Supplied Offer / Value" and "Minimal Product Clarity" in hot


def test_price_positioning_and_style_preferences_affect_decisions():
    base = {"product_name":"Serum","product_category":"skincare","product_description":"A lightweight daily serum.","benefits":["hydrated finish"]}
    premium = compile_creatives.normalize({**base,"price_positioning":"premium","visual_style_preference":["premium editorial"]})
    budget = compile_creatives.normalize({**base,"price_positioning":"budget"})
    premium_angles = [item["name"] for item in compile_creatives.choose_angles(premium)[:2]]
    budget_angles = [item["name"] for item in compile_creatives.choose_angles(budget)[:2]]
    assert premium_angles == ["Premium Product Hero", "Minimal Product Clarity"]
    assert budget_angles[0] == "Feature → Benefit"
    assert compile_creatives.build_creatives(premium)["creative_plans"][0]["visual_plan"]["visual_dna"]["name"] == "Premium Editorial"


def test_variation_strength_controls_ranked_pool_width():
    base = {"product_name":"Serum","product_category":"skincare","product_description":"A lightweight serum.","benefits":["hydrated finish"],"generation_count":8}
    low = compile_creatives.build_creatives(compile_creatives.normalize({**base,"variation_strength":"low"}))
    high = compile_creatives.build_creatives(compile_creatives.normalize({**base,"variation_strength":"high"}))
    assert low["quality_checks"]["distinct_angles"] == 2
    assert high["quality_checks"]["distinct_angles"] >= 6
    assert low["quality_checks"]["pass"] is True
    assert high["quality_checks"]["pass"] is True


def test_copy_density_follows_layout_and_evidence():
    data = compile_creatives.normalize({"product_name":"Serum","product_category":"skincare","product_description":"A full description that must not be copied into every standard creative.","benefits":["hydrated finish"],"key_features":["10% vitamin C","non-sticky texture"],"text_overlay_mode":"standard","offer_info":"Free shipping over $35","social_proof":"Lightweight and easy to use"})
    angles = {item["kind"]: item for item in compile_creatives.choose_angles(data)}
    lifestyle = compile_creatives.build_copy(data, {"kind":"lifestyle","layout":"lifestyle_story"}, "hydrated finish")
    benefit = compile_creatives.build_copy(data, {"kind":"benefit","layout":"benefit_focus"}, "hydrated finish")
    offer = compile_creatives.build_copy(data, angles["offer"], "hydrated finish")
    proof = compile_creatives.build_copy(data, angles["proof"], "hydrated finish")
    assert lifestyle["support"] == "" and lifestyle["callouts"] == []
    assert len(benefit["callouts"]) == 2 and data["product_description"] not in benefit.values()
    assert offer["support"] == data["offer_info"]
    assert proof["headline"] == data["social_proof"] and proof["support"] == ""


def test_phone_case_hypotheses_are_semantically_matched():
    data = compile_creatives.normalize({"product_name":"MagSafe Clear Case","product_category":"phone case","product_description":"A slim protective case.","benefits":["everyday device protection","easy wireless charging"],"key_features":["MagSafe compatible","raised camera edge"],"generation_count":8})
    output = compile_creatives.build_creatives(data)
    by_angle = {item["hypothesis"]["angle"]: item for item in output["creative_plans"]}
    premium = by_angle["Premium Product Hero"]
    problem = by_angle["Problem → Solution"]
    assert premium["hypothesis"]["audience"] == "minimal accessory buyers"
    assert "studio" in premium["visual_plan"]["scene"] or "minimal desk" in premium["visual_plan"]["scene"]
    assert "gift" not in premium["hypothesis"]["audience"].lower()
    assert "wireless charging" not in premium["visual_plan"]["scene"].lower()
    assert problem["hypothesis"]["audience"] == "device protection shoppers"
    assert "protection" in problem["visual_plan"]["scene"]


def test_skincare_and_usb_hypotheses_match_angle_semantics():
    skincare = compile_creatives.build_creatives(compile_creatives.normalize({"product_name":"Daily Glow Serum","product_category":"skincare serum","product_description":"A lightweight daily serum.","benefits":["hydrated finish","more even-looking tone"],"key_features":["lightweight texture","10% vitamin C"],"generation_count":8}))
    skin_by_angle = {item["hypothesis"]["angle"]: item for item in skincare["creative_plans"]}
    assert skin_by_angle["Feature → Benefit"]["hypothesis"]["audience"] == "ingredient-aware shoppers"
    assert "texture" in skin_by_angle["Feature → Benefit"]["visual_plan"]["scene"]
    assert "morning" in skin_by_angle["UGC Real Use"]["visual_plan"]["scene"]
    assert skin_by_angle["Premium Product Hero"]["hypothesis"]["audience"] == "premium skincare shoppers"

    electronics = compile_creatives.build_creatives(compile_creatives.normalize({"product_name":"USB-C 7-in-1 Hub","product_category":"electronics USB-C hub","product_description":"A compact multi-port hub.","benefits":["reduce cable switching","connect more desk accessories"],"generation_count":8}))
    usb_by_angle = {item["hypothesis"]["angle"]: item for item in electronics["creative_plans"]}
    assert usb_by_angle["Problem → Solution"]["hypothesis"]["audience"] == "productivity users"
    assert "cable-clutter" in usb_by_angle["Problem → Solution"]["visual_plan"]["scene"]
    assert "connection" in usb_by_angle["Product Demonstration"]["visual_plan"]["scene"]


def test_eight_creative_batches_have_distinct_category_specific_headlines():
    samples = [
        {"product_name":"MagSafe Clear Case","product_category":"phone case","product_description":"A slim protective case.","benefits":["everyday device protection","easy wireless charging"],"key_features":["MagSafe compatible"],"generation_count":8},
        {"product_name":"Daily Glow Serum","product_category":"skincare serum","product_description":"A lightweight serum.","benefits":["hydrated finish","more even-looking tone"],"key_features":["lightweight texture"],"generation_count":8},
        {"product_name":"USB-C Hub","product_category":"electronics USB-C hub","product_description":"A compact multi-port hub.","benefits":["reduce cable switching","connect more desk accessories"],"key_features":["7 ports"],"generation_count":8},
    ]
    for sample in samples:
        output = compile_creatives.build_creatives(compile_creatives.normalize(sample))
        headlines = [item["visual_plan"]["copy"]["headline"] for item in output["creative_plans"]]
        assert len(set(headlines)) >= 6
        assert "Ready for Every Day" not in headlines
        assert output["quality_checks"]["pass"] is True


def test_hair_dryer_image_only_never_invents_claims():
    data = compile_creatives.normalize({"product_name":"Compact Hair Dryer","product_category":"hair dryer","product_description":"Product reference image only.","reference_image":"hair-dryer.png","generation_count":8})
    output = compile_creatives.build_creatives(data)
    forbidden = ["rpm", "faster", "quiet motor", "temperature control", "heat damage", "all hair types", "salon", "before", "after"]
    angles = {item["hypothesis"]["angle"].lower() for item in output["creative_plans"]}
    assert output["input_summary"]["claim_mode"] == "visual_only"
    for item in output["creative_plans"]:
        positive = item["render_prompt"].split("AVOID:", 1)[0].lower()
        assert all(term not in positive for term in forbidden)
    assert not any("before" in angle or "after" in angle or "comparison" in angle for angle in angles)
    assert all(item["evidence_lock"]["used_claims"] == [] for item in output["creative_plans"])
    assert output["quality_checks"]["pass"] is True


def test_supplied_numeric_spec_is_allowed_without_extra_numbers():
    data = compile_creatives.normalize({"product_name":"Compact Hair Dryer","product_category":"hair dryer","product_description":"A compact dryer.","supplied_specs":["110000 RPM"],"generation_count":8})
    output = compile_creatives.build_creatives(data)
    positive = " ".join(item["render_prompt"].split("AVOID:",1)[0] for item in output["creative_plans"])
    assert "110000 RPM" in positive
    assert "3×" not in positive and "2 minutes" not in positive and "dB" not in positive
    assert all(item["quality_check"]["pass"] is True for item in output["creative_plans"])


def test_supplied_benefit_is_not_expanded_into_stronger_claims():
    data = compile_creatives.normalize({"product_name":"Compact Hair Dryer","product_category":"hair dryer","product_description":"A compact dryer.","benefits":["fast drying"],"generation_count":8})
    output = compile_creatives.build_creatives(data)
    positive = " ".join(item["render_prompt"].split("AVOID:",1)[0] for item in output["creative_plans"]).lower()
    assert "fast drying" in positive
    assert "3× faster" not in positive and "dries in 2 minutes" not in positive and "heat damage" not in positive
    assert output["quality_checks"]["pass"] is True


def test_before_after_requires_explicit_evidence():
    base = {"product_name":"Compact Hair Dryer","product_category":"hair dryer","product_description":"A compact dryer.","benefits":["fast drying"],"angle_preferences":["Before After Transformation"]}
    blocked = compile_creatives.choose_angles(compile_creatives.normalize(base))
    allowed = compile_creatives.choose_angles(compile_creatives.normalize({**base,"before_after_evidence":["User supplied paired result images"]}))
    assert all("Before After" not in item["name"] for item in blocked)
    assert any("Before After" in item["name"] for item in allowed)


def test_proof_and_offer_language_require_sources():
    base = {"product_name":"Compact Hair Dryer","product_category":"hair dryer","product_description":"A compact dryer.","benefits":["fast drying"],"generation_count":8}
    without = compile_creatives.build_creatives(compile_creatives.normalize(base))
    without_text = " ".join(item["render_prompt"] for item in without["creative_plans"]).lower()
    without_angles = {item["hypothesis"]["angle"] for item in without["creative_plans"]}
    assert "Supplied Social Proof" not in without_angles and "Supplied Offer / Value" not in without_angles
    assert all(term not in without_text for term in ("customer quote", "rating", "free shipping", "discount", "limited time"))

    supplied = compile_creatives.normalize({**base,"social_proof":"Verified buyer: easy to use","offer_info":"Free shipping over $35"})
    eligible = {item["kind"] for item in compile_creatives.choose_angles(supplied)}
    assert {"proof", "offer"} <= eligible


def test_quality_scanner_rejects_unsupported_claim_patterns():
    data = compile_creatives.normalize({"product_name":"Compact Hair Dryer","product_category":"hair dryer","product_description":"Reference image only."})
    findings = compile_creatives.unsupported_claim_findings(data, "PRODUCT: Compact Hair Dryer. TEXT: 110,000 RPM. 3× faster. Works for all hair types. AVOID: clutter.")
    assert any("numeric claim" in finding for finding in findings)
    assert any("all hair types" in finding for finding in findings)


def test_copy_tiers_allow_creative_language_without_claim_evidence():
    data = compile_creatives.normalize({"product_name":"City Sling","product_category":"apparel bag","product_description":"Product image only."})
    copy = compile_creatives.visual_only_copy(data, {"name":"Lifestyle Context"}, "city commute")
    tiers = compile_creatives.classify_copy(data, copy)
    assert copy["headline"] == "BUILT AROUND YOUR ROUTINE"
    assert tiers["headline"] == "creative_lifestyle"
    assert tiers["support"] == "soft_benefit"
    assert compile_creatives.unsupported_hard_copy_findings(data, copy) == []


def test_hard_claim_still_requires_matching_evidence():
    without = compile_creatives.normalize({"product_name":"City Sling","product_category":"apparel bag","product_description":"Product image only."})
    hard_copy = {"headline":"WATERPROOF","support":"","callouts":[],"cta":""}
    assert compile_creatives.classify_copy_tier(without, "WATERPROOF") == "hard_claim"
    assert compile_creatives.unsupported_hard_copy_findings(without, hard_copy)

    supplied = compile_creatives.normalize({"product_name":"City Sling","product_category":"apparel bag","product_description":"Supplied product facts.","verified_facts":["waterproof"]})
    assert compile_creatives.unsupported_hard_copy_findings(supplied, hard_copy) == []

    material_copy = {"headline":"Made from full-grain leather","support":"","callouts":[],"cta":""}
    assert compile_creatives.unsupported_hard_copy_findings(without, material_copy)


def test_visual_only_batch_uses_art_directed_layouts_and_copy_hierarchy():
    data = compile_creatives.normalize({"product_name":"Compact Hair Dryer","product_category":"hair dryer","product_description":"Product image only.","reference_image":"dryer.png","generation_count":8})
    output = compile_creatives.build_creatives(data)
    layouts = {item["visual_plan"]["layout"] for item in output["creative_plans"]}
    assert {"L11 Editorial Poster", "L12 Detail Crop", "L13 Asymmetric Grid"} <= layouts
    assert all(item["visual_plan"]["typography"] for item in output["creative_plans"])
    assert all(item["visual_plan"]["graphic_structure"] for item in output["creative_plans"])
    assert all("DESIGN:" in item["render_prompt"] for item in output["creative_plans"])
    assert all(item["evidence_lock"]["used_claims"] == [] for item in output["creative_plans"])
    assert output["quality_checks"]["pass"] is True
