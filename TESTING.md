# SwiftVisa Test Suite Documentation

## Overview
This document describes the comprehensive test suite for the SwiftVisa visa eligibility evaluator, covering inference logic, LLM integration, and Streamlit UI helpers.

## Test Runner
- **Location:** `src/run_unit_tests.py`
- **Command:** `python run_unit_tests.py` (no pytest dependency required)
- **Result:** All 18 tests pass

## Test Categories

### 1. Heuristic Assessment Tests (4 tests)
Tests the deterministic fallback logic used when no LLM API keys are configured.

- **test_heuristic_f1_missing_fields:** Validates that F1 profiles with incomplete information return `Insufficient Data` and list missing fields (e.g., `f1.i20_issued`, `f1.proof_of_funds_amount`).
- **test_heuristic_f1_complete:** Confirms F1 profiles with all required fields (university_acceptance=Yes, i20_issued=Yes, proof_of_funds_amount provided) return `Likely Eligible` with 80% confidence.
- **test_heuristic_h1b_no_job:** Ensures H1B profiles without a job offer return `Insufficient Data` and list `h1.employer_name` and `h1.job_offer` as missing.
- **test_heuristic_b1b2_with_return:** Verifies B1/B2 profiles with return ticket and business purpose return `Likely Eligible` with 65% confidence.

### 2. JSON Parsing and Normalization Tests (3 tests)
Tests the robustness of output parsing from LLM responses and normalization of data types.

- **test_normalize_parsed_various_shapes:** Validates that `_normalize_parsed()` correctly handles various data shapes (e.g., "85%" → 85, "[1,2]" → [1,2]), even when keys are capitalized (Decision vs decision).
- **test_parse_json_from_text_direct_json:** Ensures direct JSON parsing works for standard JSON strings.
- **test_parse_json_from_text_embedded_json:** Confirms that JSON embedded in human-readable text is extracted and parsed correctly.

### 3. RAG Pipeline with Mocked LLM Tests (3 tests)
Tests end-to-end `run_rag_for_query()` behavior with mocked LLM and retrieval.

- **test_run_rag_for_query_with_mocked_gemini:** Mocks both `retrieve()` and `call_gemini()` to test full RAG pipeline with controlled LLM output. Validates that structured JSON from the LLM is correctly parsed and returned (decision, confidence, missing_information, citations).
- **test_run_rag_for_query_fallback_to_heuristic:** Verifies that when no API keys are configured, `run_rag_for_query()` gracefully falls back to the deterministic heuristic.
- **test_run_rag_for_query_with_missing_info_return:** Tests that when the LLM returns `missing_information` in its JSON, that field is correctly passed through and is available for the UI to prompt the user.

### 4. Streamlit Helper Tests (8 tests)
Tests the UI helpers that manage visa category detection and user profile merging.

#### Visa Category Detection (5 tests)
- **test_get_category_f1:** Ensures `get_category("F1 Student")`, `get_category("student")`, and `get_category("F1")` all return `"f1"`.
- **test_get_category_h1:** Confirms H1B/work visa types map to `"h1"`.
- **test_get_category_b1b2:** Validates B1, B2, and tourist visa types map to `"b1b2"`.
- **test_get_category_k1:** Ensures K1 and fiance visa types map to `"k1"`, including accent-handling (fiancé).
- **test_get_category_other:** Confirms unknown visa types and empty/None inputs return `"other"`.

#### User Profile Merging (3 tests)
- **test_merge_extra_new_category:** Validates that merging into a new category correctly creates the nested structure in `user_profile["extra"]`.
- **test_merge_extra_existing_category:** Ensures merging into an existing category updates fields without overwriting unrelated ones.
- **test_merge_extra_overwrites:** Confirms that existing values are overwritten when the same key is merged.

## Running Tests

### Quick Run (No Dependencies)
```powershell
cd D:\SwiftVisa\src
python run_unit_tests.py
```

### With pytest (if installed)
```powershell
cd D:\SwiftVisa
python -m pip install pytest
pytest -q src/tests/test_inference.py -v
```

## Test Coverage Summary
| Category | Tests | Status |
|----------|-------|--------|
| Heuristic Assessment | 4 | ✅ Pass |
| JSON Parsing | 3 | ✅ Pass |
| RAG Pipeline (Mocked LLM) | 3 | ✅ Pass |
| Streamlit Helpers | 8 | ✅ Pass |
| **Total** | **18** | **✅ All Pass** |

## Key Testing Patterns

### 1. Mocking the LLM (`call_gemini`)
```python
from unittest.mock import patch
mock_response = json.dumps({
    "decision": "Likely Eligible",
    "confidence": 88,
    "missing_information": []
})
with patch("inference_with_gemini.call_gemini", return_value=mock_response):
    result = run_rag_for_query(user_profile, "query")
```

### 2. Mocking Document Retrieval
```python
with patch("inference_with_gemini.retrieve", return_value=[]):
    # Tests run without loading vectorstore or embeddings
    result = run_rag_for_query(user_profile, "query")
```

### 3. Testing Fallback to Heuristic
When no API keys are configured, the system automatically uses the deterministic heuristic:
```python
# Tests can rely on heuristic behavior without mocking
result = run_rag_for_query(user_profile, "query")
# Will return structured output with missing_information
```

## Manual Testing Checklist

Use the Streamlit UI to manually test end-to-end flows:

1. **F1 Student - Missing Fields**
   - Select F1 Student visa type
   - Leave i20_issued as "Unknown" and omit proof_of_funds_amount
   - Submit → expect "Insufficient Data" decision and missing field prompts

2. **F1 Student - Complete**
   - Fill all F1 fields with realistic values
   - Submit → expect "Likely Eligible" decision

3. **H1B - No Job Offer**
   - Select H1B Work visa type
   - Set job_offer to "No"
   - Submit → expect "Insufficient Data" with missing field prompts

4. **B1/B2 Visitor - Return Ticket**
   - Select B1/B2 Visitor visa type
   - Fill purpose and duration
   - Set return_ticket to "Yes"
   - Submit → expect "Likely Eligible" decision

## CI/CD Integration
Tests can be integrated into CI/CD pipelines:
```powershell
# GitHub Actions, Azure Pipelines, etc.
python src/run_unit_tests.py
if ($LASTEXITCODE -ne 0) { exit 1 }
```

## Future Enhancements
- Add Playwright/Selenium tests for full end-to-end UI automation
- Add performance benchmarks for retrieval and LLM latency
- Expand heuristic test cases for edge cases and boundary conditions
- Add property-based testing for input validation
