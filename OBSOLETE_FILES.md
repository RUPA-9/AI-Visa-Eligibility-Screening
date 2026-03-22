# SwiftVisa - Obsolete Files That Can Be Deleted

Based on audit of the project, the following files are no longer needed and can be safely removed:

## Python Scripts (Replaced or Superseded)

### Test/Development Scripts (REMOVE)
- `src/run_unit_tests.py` — replaced by `comprehensive_test_suite.py` and `focused_test_suite.py`
- `src/visa_tests.py` — old unit test file; superseded by comprehensive harness
- `src/visa_tests_advanced.py` — old advanced test; superseded by comprehensive harness
- `src/test_queries.py` — old test query script; replaced by `STREAMLIT_TEST_QUERIES.md`
- `src/comprehensive_test.py` — duplicate/old version of `comprehensive_test_suite.py`
- `src/debug_llm_response.py` — debugging script; no longer needed post-refinement
- `src/tests/test_inference.py` — old unit test; functionality integrated into comprehensive suite

### Legacy/One-Time Scripts (OPTIONAL KEEP)
- `src/cleaning_script.py` — used for initial data cleaning; kept for reference only
- `src/rename_fetched_files.py` — one-time utility for renaming fetched files; can delete after use
- `src/fetch_and_add_docs.py` — one-time fetch script; keep if you plan more fetches, otherwise delete

### Deprecated Inference (REMOVE)
- `src/rag_inference.py` — old RAG pipeline; replaced by `inference_with_gemini.py`

### Old App UI (REMOVE)
- `src/streamlit_app.py` — old Streamlit version; superseded by current `app.py`

---

## Data/Log Files (REMOVE)

### Temporary Logs
- `logs/last_raw_output.txt` — temporary debug log; can delete
- `logs/queries_gemini.jsonl` — old query log from testing; can delete if not needed for audit
- `logs/visa_test_results.jsonl` — old test results; superseded by `test_results.json`

### Data Artifacts (OPTIONAL)
- `src/data/cleaned/` — if this directory contains intermediate/duplicate processed files, can delete
- `src/logs/` — if this is a duplicate of `/logs`, can delete

---

## Documentation (OPTIONAL KEEP)

### Keep All (Core Documentation)
- `TEST_CASES.md` — comprehensive test case reference; KEEP
- `TESTING.md` — testing guide; KEEP
- `QUICK_START_TESTS.md` — quickstart; KEEP
- `STREAMLIT_TEST_QUERIES.md` — newly created real-world queries; KEEP

### Keep Conditionally
- `AI SwiftVisa (1).pdf` — if this is your project proposal/spec, KEEP; otherwise delete

---

## Recommended Deletion (Safe to Remove)

### Immediate cleanup (highest priority):
```bash
rm src/run_unit_tests.py
rm src/visa_tests.py
rm src/visa_tests_advanced.py
rm src/test_queries.py
rm src/comprehensive_test.py
rm src/debug_llm_response.py
rm src/rag_inference.py
rm src/streamlit_app.py
rm src/tests/test_inference.py
rm logs/last_raw_output.txt
rm logs/queries_gemini.jsonl
rm logs/visa_test_results.jsonl
```

### Post-fetch cleanup (after confirming no more fetches needed):
```bash
rm src/rename_fetched_files.py
rm src/fetch_and_add_docs.py
```

### One-time script (keep for future data processing):
```bash
# Keep: src/cleaning_script.py (for reference if data needs re-cleaning)
# Keep: src/embeddings_script.py (for re-indexing after adding documents)
```

---

## Final Project Structure (After Cleanup)

```
SwiftVisa/
├── .env
├── .git/
├── .gitignore
├── .streamlit/
├── AI SwiftVisa (1).pdf
├── data/
│   ├── doc_ids.npy
│   ├── visa_metadata.json
│   ├── visa_policy_index.faiss
│   ├── cleaned_policies/
│   └── policies/
├── logs/ (mostly empty)
├── src/
│   ├── app.py ✓ (main Streamlit app)
│   ├── inference_with_gemini.py ✓ (core RAG + heuristics)
│   ├── embeddings_script.py ✓ (index building)
│   ├── cleaning_script.py (data prep reference)
│   ├── comprehensive_test_suite.py ✓ (test harness)
│   ├── focused_test_suite.py ✓ (focused tests)
│   └── vector_store/
│       ├── index.faiss
│       └── metadata.json
├── STREAMLIT_TEST_QUERIES.md ✓ (test cases for manual use)
├── TEST_CASES.md ✓ (comprehensive test reference)
├── TESTING.md ✓ (testing guide)
├── QUICK_START_TESTS.md ✓ (quickstart)
└── venv/ (virtual environment)
```

✓ = Keep and use in production
- = Safe to delete
