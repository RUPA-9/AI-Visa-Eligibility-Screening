import traceback
import json
from unittest.mock import patch, MagicMock

from inference_with_gemini import (
    heuristic_assessment, _normalize_parsed, run_rag_for_query, parse_json_from_text
)

# Try to import app helpers; this will fail gracefully if streamlit is not fully configured
try:
    from app import get_category, merge_extra
except Exception:
    # Fallback in case we're in a test-only environment without full streamlit setup
    def get_category(visa_type: str) -> str:
        vt = visa_type.lower() if visa_type else ""
        if "f1" in vt or "student" in vt:
            return "f1"
        if "h1" in vt or "work" in vt:
            return "h1"
        if "b1" in vt or "b2" in vt or "tourist" in vt:
            return "b1b2"
        if "k1" in vt or "fiance" in vt or "fianc" in vt:
            return "k1"
        return "other"

    def merge_extra(user_profile, category, additions):
        if "extra" not in user_profile:
            user_profile["extra"] = {}
        if category not in user_profile["extra"]:
            user_profile["extra"][category] = {}
        user_profile["extra"][category].update(additions)


# ==================== Tests for inference_with_gemini ====================

def test_heuristic_f1_missing_fields():
    user_profile = {
        "age": "22",
        "nationality": "India",
        "education": "Bachelors",
        "employment": "Student",
        "income": "0",
        "visa_type": "F1 Student",
        "extra": {
            "f1": {
                "university_acceptance": "Yes",
            }
        }
    }
    result = heuristic_assessment(user_profile, docs_used=[])
    assert isinstance(result, dict)
    assert result["decision"] == "Insufficient Data"
    assert len(result["missing_information"]) > 0
    assert any("f1" in m for m in result["missing_information"])


def test_heuristic_f1_complete():
    user_profile = {
        "age": "22",
        "nationality": "India",
        "education": "Bachelors",
        "employment": "Student",
        "income": "50000",
        "visa_type": "F1 Student",
        "extra": {
            "f1": {
                "university_acceptance": "Yes",
                "i20_issued": "Yes",
                "proof_of_funds_amount": "USD 100000",
            }
        }
    }
    result = heuristic_assessment(user_profile, docs_used=[])
    assert result["decision"] == "Likely Eligible"
    assert result["confidence"] == 80
    assert result["missing_information"] == []


def test_heuristic_h1b_no_job():
    user_profile = {
        "age": "28",
        "nationality": "India",
        "education": "Bachelors",
        "employment": "Software Engineer",
        "income": "0",
        "visa_type": "H1B Work",
        "extra": {
            "h1": {
                "job_offer": "No",
            }
        }
    }
    result = heuristic_assessment(user_profile, docs_used=[])
    assert result["decision"] == "Insufficient Data"
    assert "h1.employer_name" in result["missing_information"]


def test_heuristic_b1b2_with_return():
    user_profile = {
        "age": "40",
        "nationality": "India",
        "education": "Bachelors",
        "employment": "Business Owner",
        "income": "200000",
        "visa_type": "B1/B2 Visitor",
        "extra": {
            "b1b2": {
                "travel_purpose": "business",
                "trip_duration_days": 10,
                "return_ticket": "Yes",
            }
        }
    }
    result = heuristic_assessment(user_profile, docs_used=[])
    assert result["decision"] == "Likely Eligible"
    assert result["confidence"] == 65
    assert result["missing_information"] == []


def test_normalize_parsed_various_shapes():
    raw = {
        "Decision": "Likely Eligible",
        "Explanation": "Cited documents indicate eligibility.",
        "Confidence": "85%",
        "citations": "[1,2]",
        "missing": "[]"
    }
    norm = _normalize_parsed(raw)
    assert norm["decision"] == "Likely Eligible"
    assert norm["confidence"] == 85
    assert isinstance(norm["citations"], list)
    assert isinstance(norm["missing_information"], list)


def test_parse_json_from_text_direct_json():
    raw_json = '{"decision": "Likely Ineligible", "confidence": 20, "explanation": "Test", "citations": [1], "missing_information": []}'
    parsed = parse_json_from_text(raw_json)
    assert parsed["decision"] == "Likely Ineligible"
    assert parsed["confidence"] == 20


def test_parse_json_from_text_embedded_json():
    text = "Some preamble\n{\n  \"decision\": \"Sufficient\",\n  \"confidence\": 50\n}\nSome postamble"
    parsed = parse_json_from_text(text)
    assert parsed["decision"] == "Sufficient"


def test_run_rag_for_query_with_mocked_gemini():
    """Test run_rag_for_query with mocked call_gemini and retrieve."""
    user_profile = {
        "age": "25",
        "nationality": "Canada",
        "education": "Masters",
        "employment": "Unemployed",
        "income": "0",
        "visa_type": "F1 Student",
        "extra": {
            "f1": {
                "university_acceptance": "Yes",
                "i20_issued": "Yes",
                "proof_of_funds_amount": "USD 50000",
            }
        }
    }

    # Mock the retrieve function to return empty list (no vectorstore needed)
    mock_llm_response = json.dumps({
        "decision": "Likely Eligible",
        "explanation": "Applicant meets F1 requirements.",
        "confidence": 88,
        "citations": [1, 2],
        "missing_information": []
    })

    with patch("inference_with_gemini.retrieve", return_value=[]):
        with patch("inference_with_gemini.call_gemini", return_value=mock_llm_response):
            result = run_rag_for_query(user_profile, "F1 student visa requirements")
            assert result["decision"] == "Likely Eligible"
            assert result["confidence"] == 88
            assert result["missing_information"] == []


def test_run_rag_for_query_fallback_to_heuristic():
    """Test that run_rag_for_query falls back to heuristic when no API keys set."""
    user_profile = {
        "age": "30",
        "nationality": "Brazil",
        "education": "Bachelors",
        "employment": "Consultant",
        "income": "100000",
        "visa_type": "B1/B2 Visitor",
        "extra": {
            "b1b2": {
                "travel_purpose": "business",
                "trip_duration_days": 5,
                # missing return_ticket
            }
        }
    }

    # Mock retrieve to return empty list; set env vars to empty so no API keys are found
    with patch("inference_with_gemini.retrieve", return_value=[]):
        with patch("inference_with_gemini.os.getenv") as mock_getenv:
            # Mock os.getenv to return None for all API keys
            mock_getenv.side_effect = lambda key, default=None: None if "KEY" in key else default
            result = run_rag_for_query(user_profile, "B1/B2 visitor visa")
            # Should use heuristic and return Insufficient Data
            assert result["decision"] == "Insufficient Data"
            # The heuristic checks for return_ticket in b1b2, so it should be in missing_information
            assert any("return_ticket" in str(m) for m in result["missing_information"])


def test_run_rag_for_query_with_missing_info_return():
    """Test that run_rag_for_query properly parses and returns missing_information from LLM."""
    user_profile = {
        "age": "35",
        "nationality": "Mexico",
        "education": "Bachelors",
        "employment": "Doctor",
        "income": "80000",
        "visa_type": "H1B Work",
        "extra": {}
    }

    mock_llm_response = json.dumps({
        "decision": "Insufficient Data",
        "explanation": "Need to verify job offer and employer details.",
        "confidence": 30,
        "citations": [],
        "missing_information": ["h1.job_offer", "h1.employer_name", "h1.years_experience"]
    })

    with patch("inference_with_gemini.retrieve", return_value=[]):
        with patch("inference_with_gemini.call_gemini", return_value=mock_llm_response):
            result = run_rag_for_query(user_profile, "H1B work visa requirements")
            assert result["decision"] == "Insufficient Data"
            assert "h1.job_offer" in result["missing_information"]
            assert "h1.employer_name" in result["missing_information"]


# ==================== Tests for app.py helpers ====================

def test_get_category_f1():
    assert get_category("F1 Student") == "f1"
    assert get_category("student") == "f1"
    assert get_category("F1") == "f1"


def test_get_category_h1():
    assert get_category("H1B Work") == "h1"
    assert get_category("h1b") == "h1"
    assert get_category("work") == "h1"


def test_get_category_b1b2():
    assert get_category("B1/B2 Visitor") == "b1b2"
    assert get_category("b1") == "b1b2"
    assert get_category("b2") == "b1b2"
    assert get_category("tourist") == "b1b2"


def test_get_category_k1():
    assert get_category("K1 Fiance") == "k1"
    assert get_category("k1") == "k1"
    assert get_category("fiance") == "k1"
    assert get_category("fiancé") == "k1"


def test_get_category_other():
    assert get_category("Unknown Visa") == "other"
    assert get_category("") == "other"
    assert get_category(None) == "other"


def test_merge_extra_new_category():
    user_profile = {
        "age": "25",
        "nationality": "India",
        "extra": {}
    }
    merge_extra(user_profile, "f1", {"school_name": "MIT", "i20_issued": "Yes"})
    assert user_profile["extra"]["f1"]["school_name"] == "MIT"
    assert user_profile["extra"]["f1"]["i20_issued"] == "Yes"


def test_merge_extra_existing_category():
    user_profile = {
        "age": "25",
        "extra": {
            "f1": {
                "school_name": "MIT"
            }
        }
    }
    merge_extra(user_profile, "f1", {"i20_issued": "Yes"})
    assert user_profile["extra"]["f1"]["school_name"] == "MIT"
    assert user_profile["extra"]["f1"]["i20_issued"] == "Yes"


def test_merge_extra_overwrites():
    user_profile = {
        "age": "25",
        "extra": {
            "f1": {
                "school_name": "Harvard"
            }
        }
    }
    merge_extra(user_profile, "f1", {"school_name": "Stanford"})
    assert user_profile["extra"]["f1"]["school_name"] == "Stanford"


if __name__ == "__main__":
    tests = [
        ("test_heuristic_f1_missing_fields", test_heuristic_f1_missing_fields),
        ("test_heuristic_f1_complete", test_heuristic_f1_complete),
        ("test_heuristic_h1b_no_job", test_heuristic_h1b_no_job),
        ("test_heuristic_b1b2_with_return", test_heuristic_b1b2_with_return),
        ("test_normalize_parsed_various_shapes", test_normalize_parsed_various_shapes),
        ("test_parse_json_from_text_direct_json", test_parse_json_from_text_direct_json),
        ("test_parse_json_from_text_embedded_json", test_parse_json_from_text_embedded_json),
        ("test_run_rag_for_query_with_mocked_gemini", test_run_rag_for_query_with_mocked_gemini),
        ("test_run_rag_for_query_fallback_to_heuristic", test_run_rag_for_query_fallback_to_heuristic),
        ("test_run_rag_for_query_with_missing_info_return", test_run_rag_for_query_with_missing_info_return),
        ("test_get_category_f1", test_get_category_f1),
        ("test_get_category_h1", test_get_category_h1),
        ("test_get_category_b1b2", test_get_category_b1b2),
        ("test_get_category_k1", test_get_category_k1),
        ("test_get_category_other", test_get_category_other),
        ("test_merge_extra_new_category", test_merge_extra_new_category),
        ("test_merge_extra_existing_category", test_merge_extra_existing_category),
        ("test_merge_extra_overwrites", test_merge_extra_overwrites),
    ]

    failures = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS: {name}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL: {name} - AssertionError: {e}")
            traceback.print_exc()
        except Exception as e:
            failures += 1
            print(f"ERROR: {name} - Exception: {e}")
            traceback.print_exc()

    if failures:
        print(f"\n{failures} test(s) failed")
        exit(1)
    else:
        print(f"\nAll {len(tests)} tests passed")
        exit(0)
