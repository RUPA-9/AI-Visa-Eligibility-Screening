# NEXT ACTIONS - Test Queries 9-15

Once you're ready to test the remaining queries, here's what to do:

## Testing Checklist

### Query 7 (B1/B2 Strong Ties - Business)
- [ ] Open Streamlit app (http://localhost:8501)
- [ ] Select "B1/B2 Visitor"
- [ ] Fill in form fields from query specification
- [ ] Copy output and paste below query in `STREAMLIT_TEST_QUERIES.md`
- [ ] Note: Should return "Likely Eligible (75+)"

### Query 9 (B1/B2 Weak Ties - Tourist)
- [ ] Select "B1/B2 Visitor"
- [ ] Fill in form fields (weak ties profile)
- [ ] Copy output and paste in test file
- [ ] Note: Should return "Insufficient Data" (weak ties are risky)

### Queries 10-12 (K1 Fiancé Cases)
- [ ] Select "K1 Fiance"
- [ ] Test three scenarios:
  - Query 10: Complete eligible (18 months, met in person, US sponsor)
  - Query 11: Recent (2 months, just engaged)
  - Query 12: No in-person meeting (online only)
- [ ] Record outputs for each

### Queries 13-15 (Edge Cases)
- [ ] Query 13: Multiple visa options (exploratory)
- [ ] Query 14: Status change (already in US)
- [ ] Query 15: Post-graduation OPT question
- [ ] Record all outputs

## How to Verify Results

After testing each query:

1. **Check Decision Field** - Does it match expected decision?
2. **Check Confidence** - Is it within expected range?
3. **Check Explanation** - Does it make sense?
4. **Note Missing Info** - If any, does it request missing fields?

## Quality Checks

✅ Decisions should be one of:
- "Likely Eligible"
- "Likely Ineligible"
- "Insufficient Data"

✅ Confidence should be:
- Integer 0-100
- Higher = more confident

✅ Explanations should:
- Reference relevant documents
- Mention key criteria
- Explain the reasoning

---

## Expected Timeline

- **Queries 7-9 (B1/B2)**: ~5-10 mins
- **Queries 10-12 (K1)**: ~5-10 mins
- **Queries 13-15 (Edge cases)**: ~5 mins
- **Total**: ~15-25 minutes

Once all completed, we can:
1. Update the test results summary
2. Run final comprehensive test
3. Generate production-ready report

