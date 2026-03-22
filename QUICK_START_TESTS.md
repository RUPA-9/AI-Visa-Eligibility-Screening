# Quick Reference: Running Tests

## All Tests Pass ✅ (18/18)

### Run All Tests (No Prerequisites)
```powershell
cd D:\SwiftVisa\src
python run_unit_tests.py
```

### What Gets Tested

| Component | Tests | Coverage |
|-----------|-------|----------|
| Heuristic (F1, H1B, B1B2, K1) | 4 | Fallback logic for missing LLM |
| JSON Parsing & Normalization | 3 | LLM output robustness |
| RAG Pipeline (Mocked LLM) | 3 | End-to-end with mocked calls |
| Visa Category Detection | 5 | `get_category()` function |
| User Profile Merging | 3 | `merge_extra()` function |

### Manual Testing (Interactive)
Start the Streamlit app to test the UI:
```powershell
cd D:\SwiftVisa\src
python -m streamlit run app.py --server.headless true
```
Then open: http://localhost:8501

Try these scenarios:
1. **F1 Student (incomplete)** → Expect "Insufficient Data" + missing field prompts
2. **F1 Student (complete)** → Expect "Likely Eligible"
3. **H1B (no job offer)** → Expect "Insufficient Data"
4. **B1/B2 (with return ticket)** → Expect "Likely Eligible"

Check "Show raw / debug output" checkbox to inspect the raw response structure.

### Key Features
- **No API Keys Required**: App uses deterministic heuristic fallback for offline testing
- **Mocked LLM**: Tests mock `call_gemini()` and `retrieve()` to avoid external dependencies
- **Robust Parsing**: Handles various JSON response shapes from LLMs
- **Missing Information Flow**: Properly identifies and prompts for missing user inputs

### Files
- `run_unit_tests.py` — Main test runner
- `inference_with_gemini.py` — RAG + LLM + heuristic fallback logic
- `app.py` — Streamlit UI with visa-specific fields and missing-info flow
- `TESTING.md` — Full test documentation
