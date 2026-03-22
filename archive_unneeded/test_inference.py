import json
import pytest

from inference_with_gemini import heuristic_assessment, _normalize_parsed


def test_heuristic_f1_missing_fields():
    # F1 profile missing i20 and proof_of_funds_amount should report missing keys
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
                # i20_issued missing
                # proof_of_funds_amount missing
            }
        }
    }

    result = heuristic_assessment(user_profile, docs_used=[])
    assert isinstance(result, dict)
    assert result["decision"] == "Insufficient Data"
    assert "f1.i20_issued" in result["missing_information"] or "f1.proof_of_funds_amount" in result["missing_information"]
    assert result["confidence"] <= 50


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
    assert norm["citations"] == [1, 2] or norm["citations"] == [] or all(isinstance(x, int) for x in norm["citations"])
    assert isinstance(norm["missing_information"], list)

*** End of File
