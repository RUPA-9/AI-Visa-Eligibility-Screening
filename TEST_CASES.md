# Comprehensive Test Cases for SwiftVisa Visa Eligibility Evaluator

## Test Coverage Overview

This document provides **24 comprehensive test cases** covering:
- **4 Visa Types:** F1 Student, H1B Work, B1/B2 Visitor, K1 Fiance
- **6 Scenarios per visa type:**
  1. Missing all required fields (Insufficient Data expected)
  2. Partial fields provided (Insufficient Data expected)
  3. All fields complete with positive indicators (Likely Eligible expected)
  4. All fields complete with negative indicators (Likely Ineligible expected)
  5. Edge case: Unknown/ambiguous responses
  6. Data validation and normalization

---

## Test Suite 1: F1 Student Visa (6 Tests)

### Test Case F1-001: Missing All F1-Specific Fields
**Expected Outcome:** Insufficient Data, missing field prompts for all required fields

| Field | Input | Notes |
|-------|-------|-------|
| Visa Type | F1 Student | |
| Age | 22 | Required |
| Nationality | India | Required |
| Education | Bachelors | Required |
| Employment | Student | Required |
| Income | 0 | Required |
| **F1 Fields** | | |
| University acceptance | Unknown | Missing ❌ |
| School name | (empty) | Missing ❌ |
| I-20 issued | Unknown | Missing ❌ |
| Proof of funds | (empty) | Missing ❌ |
| Test scores | (empty) | Missing ❌ |

**Steps:**
1. Select F1 Student
2. Fill general fields
3. Leave all F1 specific fields as default
4. Click "Evaluate"

**Expected Result:**
- Decision: "Insufficient Data"
- Confidence: 25 or lower
- Missing fields expander appears
- Lists missing keys: f1.university_acceptance, f1.i20_issued, f1.proof_of_funds_amount

---

### Test Case F1-002: Partial F1 Fields (Only Acceptance)
**Expected Outcome:** Insufficient Data, prompts for I-20 and proof of funds

| Field | Input |
|-------|-------|
| Visa Type | F1 Student |
| Age | 23 |
| Nationality | China |
| Education | Masters |
| Employment | Student |
| Income | 10000 |
| University acceptance | Yes ✓ |
| School name | Stanford University | ✓ |
| I-20 issued | Unknown | Missing |
| Proof of funds | (empty) | Missing |
| Test scores | TOEFL 100 | ✓ |

**Steps:**
1. Select F1 Student
2. Fill general fields
3. Set university_acceptance = Yes, school_name = Stanford University, test_scores = TOEFL 100
4. Leave I-20 and proof of funds
5. Click "Evaluate"

**Expected Result:**
- Decision: "Insufficient Data"
- Confidence: 30-40
- Missing fields: f1.i20_issued, f1.proof_of_funds_amount
- Submit missing info and fill in the fields

---

### Test Case F1-003: Complete F1 - Eligible Profile
**Expected Outcome:** Likely Eligible

| Field | Input |
|-------|-------|
| Visa Type | F1 Student |
| Age | 22 |
| Nationality | India |
| Education | Bachelors (B.Tech) |
| Employment | Student |
| Income | 50000 |
| University acceptance | Yes ✓ |
| School name | MIT |
| I-20 issued | Yes ✓ |
| Proof of funds | USD 100000 |
| Test scores | TOEFL 110 |

**Steps:**
1. Fill all fields as shown
2. Click "Evaluate"

**Expected Result:**
- Decision: "Likely Eligible" ✅
- Confidence: 75-85
- No missing fields expander
- Success message displays

---

### Test Case F1-004: Complete F1 - No I-20 (Ineligible)
**Expected Outcome:** Likely Ineligible or Insufficient Data

| Field | Input |
|-------|-------|
| Visa Type | F1 Student |
| Age | 25 |
| Nationality | Brazil |
| Education | Masters |
| Employment | Student |
| Income | 80000 |
| University acceptance | Yes |
| School name | Harvard |
| I-20 issued | No ❌ |
| Proof of funds | USD 50000 |
| Test scores | IELTS 7.5 |

**Steps:**
1. Fill all fields with I-20 = No
2. Click "Evaluate"

**Expected Result:**
- Decision: "Likely Ineligible" or "Insufficient Data"
- Confidence: 30 or lower
- Explanation mentions I-20 requirement

---

### Test Case F1-005: F1 - Ambiguous Responses (Unknown Values)
**Expected Outcome:** Insufficient Data with specific missing keys

| Field | Input |
|-------|-------|
| Visa Type | F1 Student |
| Age | 20 |
| Nationality | Vietnam |
| Education | Bachelors |
| Employment | Student |
| Income | 0 |
| University acceptance | Unknown |
| School name | Stanford |
| I-20 issued | Unknown |
| Proof of funds | USD 40000 |
| Test scores | TOEFL 95 |

**Steps:**
1. Fill fields leaving some as "Unknown"
2. Click "Evaluate"

**Expected Result:**
- Decision: "Insufficient Data"
- Missing fields are prompted for Unknown values

---

### Test Case F1-006: F1 - Data Validation (Numeric and Format)
**Expected Outcome:** Proof of funds accepted in various formats

| Field | Input |
|-------|-------|
| Visa Type | F1 Student |
| Age | 21 |
| Nationality | Japan |
| Education | Bachelors |
| Employment | Student |
| Income | 35000 |
| University acceptance | Yes |
| School name | UC Berkeley |
| I-20 issued | Yes |
| Proof of funds | "50,000 USD" or "50000" or "50k USD" |
| Test scores | TOEFL 105, IELTS 7.0 |

**Steps:**
1. Try different proof of funds formats
2. Click "Evaluate"

**Expected Result:**
- All formats accepted
- No validation errors
- Decision rendered successfully

---

## Test Suite 2: H1B Work Visa (6 Tests)

### Test Case H1B-001: Missing Job Offer and Employer
**Expected Outcome:** Insufficient Data, prompts for job details

| Field | Input |
|-------|-------|
| Visa Type | H1B Work |
| Age | 28 |
| Nationality | India |
| Education | Bachelors |
| Employment | Software Engineer |
| Income | 0 |
| Job offer | No ❌ |
| Employer name | (empty) |
| Years of experience | 0 |
| Degree equivalency | Unknown |

**Steps:**
1. Select H1B Work
2. Leave job offer as No, employer empty
3. Click "Evaluate"

**Expected Result:**
- Decision: "Insufficient Data"
- Missing fields: h1.job_offer, h1.employer_name
- Prompts to fill in missing fields

---

### Test Case H1B-002: Partial H1B (Job but No Experience)
**Expected Outcome:** Insufficient Data

| Field | Input |
|-------|-------|
| Visa Type | H1B Work |
| Age | 30 |
| Nationality | Philippines |
| Education | Masters |
| Employment | Software Engineer |
| Income | 120000 |
| Job offer | Yes ✓ |
| Employer name | Google |
| Years of experience | 0 |
| Degree equivalency | Yes |

**Steps:**
1. Fill fields with job offer = Yes
2. Leave years_experience = 0
3. Click "Evaluate"

**Expected Result:**
- Decision: "Insufficient Data" or "Likely Eligible" (depending on inference)
- May prompt for experience details

---

### Test Case H1B-003: Complete H1B - Strong Profile
**Expected Outcome:** Likely Eligible

| Field | Input |
|-------|-------|
| Visa Type | H1B Work |
| Age | 32 |
| Nationality | India |
| Education | Masters (CS) |
| Employment | Senior Software Engineer |
| Income | 250000 |
| Job offer | Yes ✓ |
| Employer name | Microsoft |
| Years of experience | 7 |
| Degree equivalency | Yes ✓ |

**Steps:**
1. Fill all H1B fields with strong credentials
2. Click "Evaluate"

**Expected Result:**
- Decision: "Likely Eligible" ✅
- Confidence: 75-85
- Success message

---

### Test Case H1B-004: Complete H1B - No Job Offer
**Expected Outcome:** Likely Ineligible

| Field | Input |
|-------|-------|
| Visa Type | H1B Work |
| Age | 29 |
| Nationality | Canada |
| Education | Bachelors |
| Employment | Unemployed |
| Income | 0 |
| Job offer | No ❌ |
| Employer name | N/A |
| Years of experience | 5 |
| Degree equivalency | Yes |

**Steps:**
1. Fill all fields with job_offer = No
2. Click "Evaluate"

**Expected Result:**
- Decision: "Likely Ineligible"
- Confidence: 25 or lower
- Explanation mentions job offer requirement

---

### Test Case H1B-005: H1B - Minimum Experience Requirement
**Expected Outcome:** Eligible with modest experience

| Field | Input |
|-------|-------|
| Visa Type | H1B Work |
| Age | 25 |
| Nationality | Mexico |
| Education | Bachelors |
| Employment | Junior Developer |
| Income | 80000 |
| Job offer | Yes |
| Employer name | Amazon |
| Years of experience | 2 |
| Degree equivalency | Yes |

**Steps:**
1. Fill with minimum experience (2 years)
2. Click "Evaluate"

**Expected Result:**
- Decision: "Likely Eligible"
- Confidence: 70-80
- Acknowledges experience

---

### Test Case H1B-006: H1B - No Degree Equivalency
**Expected Outcome:** Insufficient Data or Ineligible

| Field | Input |
|-------|-------|
| Visa Type | H1B Work |
| Age | 35 |
| Nationality | Pakistan |
| Education | Diploma |
| Employment | Software Engineer |
| Income | 150000 |
| Job offer | Yes |
| Employer name | Facebook |
| Years of experience | 10 |
| Degree equivalency | No ❌ |

**Steps:**
1. Fill with degree_equivalency = No
2. Click "Evaluate"

**Expected Result:**
- Decision: "Likely Ineligible"
- Explanation mentions bachelor's degree requirement

---

## Test Suite 3: B1/B2 Visitor Visa (6 Tests)

### Test Case B1B2-001: Missing Return Ticket
**Expected Outcome:** Insufficient Data, prompts for return ticket

| Field | Input |
|-------|-------|
| Visa Type | B1/B2 Visitor |
| Age | 45 |
| Nationality | India |
| Education | Bachelors |
| Employment | Business Owner |
| Income | 200000 |
| Travel purpose | Business |
| Trip duration | 14 |
| Invitation/host | ABC Company |
| Return ticket | No ❌ |

**Steps:**
1. Select B1/B2 Visitor
2. Leave return_ticket as No
3. Click "Evaluate"

**Expected Result:**
- Decision: "Insufficient Data"
- Missing fields: b1b2.return_ticket
- Prompts to provide return ticket proof

---

### Test Case B1B2-002: Partial B1B2 (No Invitation or Host)
**Expected Outcome:** Likely Eligible (not always required)

| Field | Input |
|-------|-------|
| Visa Type | B1/B2 Visitor |
| Age | 35 |
| Nationality | Mexico |
| Education | Bachelors |
| Employment | Manager |
| Income | 120000 |
| Travel purpose | Tourism |
| Trip duration | 7 |
| Invitation/host | (empty) |
| Return ticket | Yes ✓ |

**Steps:**
1. Fill B1B2 fields
2. Leave invitation empty (not always required)
3. Click "Evaluate"

**Expected Result:**
- Decision: "Likely Eligible" ✅
- Confidence: 65-75
- Not all fields are mandatory

---

### Test Case B1B2-003: Complete B1B2 - Business Trip
**Expected Outcome:** Likely Eligible

| Field | Input |
|-------|-------|
| Visa Type | B1/B2 Visitor |
| Age | 40 |
| Nationality | Japan |
| Education | Masters |
| Employment | Director, Tech Company |
| Income | 300000 |
| Travel purpose | Business |
| Trip duration | 10 |
| Invitation/host | XYZ Corp (US partner) |
| Return ticket | Yes ✓ |

**Steps:**
1. Fill all B1B2 fields with business purpose
2. Click "Evaluate"

**Expected Result:**
- Decision: "Likely Eligible" ✅
- Confidence: 75+
- Strong profile

---

### Test Case B1B2-004: Complete B1B2 - Tourist Trip
**Expected Outcome:** Likely Eligible

| Field | Input |
|-------|-------|
| Visa Type | B1/B2 Visitor |
| Age | 30 |
| Nationality | Brazil |
| Education | Bachelors |
| Employment | Accountant |
| Income | 80000 |
| Travel purpose | Tourism |
| Trip duration | 14 |
| Invitation/host | Friend (California) |
| Return ticket | Yes ✓ |

**Steps:**
1. Fill with tourism purpose
2. Click "Evaluate"

**Expected Result:**
- Decision: "Likely Eligible" ✅
- Confidence: 65-75
- Tourism context acknowledged

---

### Test Case B1B2-005: B1B2 - Long Duration (3+ Months)
**Expected Outcome:** Insufficient Data (may need intent documentation)

| Field | Input |
|-------|-------|
| Visa Type | B1/B2 Visitor |
| Age | 50 |
| Nationality | Germany |
| Education | Bachelors |
| Employment | Retired |
| Income | 50000 |
| Travel purpose | Medical |
| Trip duration | 90 |
| Invitation/host | Mayo Clinic |
| Return ticket | Yes |

**Steps:**
1. Fill with trip duration = 90 days
2. Click "Evaluate"

**Expected Result:**
- Decision may indicate need for additional documentation
- Confidence lower due to longer stay
- Medical context considered

---

### Test Case B1B2-006: B1B2 - Medical Travel
**Expected Outcome:** Likely Eligible with medical context

| Field | Input |
|-------|-------|
| Visa Type | B1/B2 Visitor |
| Age | 65 |
| Nationality | UK |
| Education | Bachelors |
| Employment | Retired |
| Income | 100000 |
| Travel purpose | Medical |
| Trip duration | 30 |
| Invitation/host | Hospital name |
| Return ticket | Yes ✓ |

**Steps:**
1. Fill with medical purpose
2. Click "Evaluate"

**Expected Result:**
- Decision: "Likely Eligible"
- Medical travel acknowledged
- Confidence appropriate for medical tourism

---

## Test Suite 4: K1 Fiance Visa (6 Tests)

### Test Case K1-001: Missing US Citizen Sponsor
**Expected Outcome:** Insufficient Data

| Field | Input |
|-------|-------|
| Visa Type | K1 Fiance |
| Age | 26 |
| Nationality | Philippines |
| Education | Bachelors |
| Employment | Secretary |
| Income | 0 |
| US citizen sponsor | No ❌ |
| Met in person | Unknown |
| Relationship length | 0 |
| Evidence list | (empty) |

**Steps:**
1. Select K1 Fiance
2. Leave US citizen sponsor as No
3. Click "Evaluate"

**Expected Result:**
- Decision: "Insufficient Data" or "Likely Ineligible"
- Missing: k1.us_citizen_sponsor
- Cannot proceed without sponsor

---

### Test Case K1-002: Sponsor but Never Met
**Expected Outcome:** Insufficient Data or Ineligible

| Field | Input |
|-------|-------|
| Visa Type | K1 Fiance |
| Age | 24 |
| Nationality | Colombia |
| Education | Bachelors |
| Employment | Teacher |
| Income | 25000 |
| US citizen sponsor | Yes ✓ |
| Met in person | No ❌ |
| Relationship length | 6 |
| Evidence list | Chat messages, photos |

**Steps:**
1. Fill with sponsor = Yes
2. Set met_in_person = No
3. Click "Evaluate"

**Expected Result:**
- Decision: "Likely Ineligible" or "Insufficient Data"
- Explanation mentions in-person meeting requirement
- Evidence alone not sufficient

---

### Test Case K1-003: Complete K1 - Eligible Profile
**Expected Outcome:** Likely Eligible

| Field | Input |
|-------|-------|
| Visa Type | K1 Fiance |
| Age | 27 |
| Nationality | Ukraine |
| Education | Masters |
| Employment | Engineer |
| Income | 0 |
| US citizen sponsor | Yes ✓ |
| Met in person | Yes ✓ |
| Relationship length | 18 |
| Evidence list | Passport stamps, photos, plane tickets, chat history |

**Steps:**
1. Fill all K1 fields completely
2. Provide comprehensive evidence
3. Click "Evaluate"

**Expected Result:**
- Decision: "Likely Eligible" ✅
- Confidence: 70-80
- Evidence reviewed

---

### Test Case K1-004: K1 - Recent Meeting (< 3 months)
**Expected Outcome:** Likely Eligible if other conditions met

| Field | Input |
|-------|-------|
| Visa Type | K1 Fiance |
| Age | 25 |
| Nationality | Thailand |
| Education | Bachelors |
| Employment | Sales |
| Income | 20000 |
| US citizen sponsor | Yes |
| Met in person | Yes |
| Relationship length | 2 |
| Evidence list | Recent trip photos, tickets, communication logs |

**Steps:**
1. Fill with relationship_length = 2 months
2. Include recent meeting evidence
3. Click "Evaluate"

**Expected Result:**
- Decision: "Likely Eligible"
- Confidence: 65-75
- Recent but documented meeting

---

### Test Case K1-005: K1 - Long Relationship (2+ years)
**Expected Outcome:** Likely Eligible - strong case

| Field | Input |
|-------|-------|
| Visa Type | K1 Fiance |
| Age | 30 |
| Nationality | Canada |
| Education | Masters |
| Employment | Consultant |
| Income | 150000 |
| US citizen sponsor | Yes ✓ |
| Met in person | Yes ✓ |
| Relationship length | 24 |
| Evidence list | Multiple visits, photos, communications, engagement ring photo, wedding plans |

**Steps:**
1. Fill with 24-month relationship
2. Comprehensive evidence
3. Click "Evaluate"

**Expected Result:**
- Decision: "Likely Eligible" ✅
- Confidence: 80+
- Strong documented relationship

---

### Test Case K1-006: K1 - Sponsor with Financial Verification
**Expected Outcome:** Eligible with income consideration

| Field | Input |
|-------|-------|
| Visa Type | K1 Fiance |
| Age | 28 |
| Nationality | Vietnam |
| Education | Bachelors |
| Employment | Nurse |
| Income | 60000 |
| US citizen sponsor | Yes |
| Met in person | Yes |
| Relationship length | 12 |
| Evidence list | Affidavit of support form (I-864), sponsor's financial docs, relationship documentation |

**Steps:**
1. Fill all fields
2. Mention I-864 affidavit in evidence
3. Click "Evaluate"

**Expected Result:**
- Decision: "Likely Eligible"
- Financial support acknowledged
- Confidence: 75-85

---

## Cross-Cutting Test Cases (4 Tests)

### Test Case XC-001: Data Type Validation - Age Field
**Purpose:** Validate age normalization and input handling

| Field | Input | Expected Behavior |
|-------|-------|-------------------|
| Age | "25" (string) | Converted to int, processed correctly |
| Age | "twenty-five" | Treated as text, not numeric |
| Age | "25.5" | Handled (rounded or truncated) |
| Age | (empty) | Treated as unknown |

**Steps:**
1. Try different age formats
2. Observe how system handles them
3. Verify no crashes or errors

**Expected Result:**
- All inputs handled gracefully
- Numeric strings converted
- Non-numeric strings preserved
- No validation errors

---

### Test Case XC-002: Session State Persistence - Form Reset
**Purpose:** Verify data persistence across reruns

**Steps:**
1. Fill form completely
2. Click "Evaluate"
3. Don't submit missing info
4. Click "Cancel"
5. Change visa type
6. Click back to original visa type

**Expected Result:**
- Previous visa type data cleared
- New visa type fields render fresh
- No data leakage between visa types

---

### Test Case XC-003: Missing Information Flow - Multi-Step
**Purpose:** Verify complete missing info workflow

**Steps:**
1. F1 Student: Leave all fields Unknown
2. Click "Evaluate" → See all missing fields
3. Fill in first batch of missing fields
4. Click "Submit missing info"
5. If still missing, fill second batch
6. Click "Submit missing info" again

**Expected Result:**
- Each step prompts for correct missing fields
- Explanation persists
- Final result appears without disappearing
- No modal/explanation loss

---

### Test Case XC-004: Debug Output Inspection
**Purpose:** Verify raw output transparency

**Steps:**
1. Fill any form completely
2. Click "Evaluate"
3. Check "Show raw / debug output"
4. Inspect JSON structure

**Expected Result:**
```json
{
  "decision": "string",
  "confidence": "number",
  "explanation": "string",
  "citations": [1, 2, ...],
  "missing_information": ["string", ...]
}
```
- All expected keys present
- No null/undefined values
- Valid JSON format
- citations are integers
- missing_information is array

---

## Test Execution Checklist

### Before Testing
- [ ] Streamlit app running: `python -m streamlit run src/app.py`
- [ ] App accessible at http://localhost:8501
- [ ] Browser cache cleared
- [ ] Console open (F12) for error monitoring

### During Testing
- [ ] Record actual vs expected outcomes
- [ ] Note any error messages
- [ ] Check browser console for JavaScript errors
- [ ] Verify page load time (should be < 3s)
- [ ] Check that no fields lose values unexpectedly

### After Each Test
- [ ] Verify decision is one of: "Likely Eligible", "Likely Ineligible", "Insufficient Data"
- [ ] Verify confidence is 0-100
- [ ] Verify explanation is non-empty
- [ ] Check missing_information format (array of strings)
- [ ] Inspect raw output if decision seems wrong

### After All Tests
- [ ] Document any failures
- [ ] Note any edge cases not covered
- [ ] Test performance with large inputs
- [ ] Verify no session state leakage between forms

---

## Issue Tracking Template

For each failed test, record:

```
Test Case: [ID]
Expected: [Outcome]
Actual: [What happened]
Steps to Reproduce: [Detailed steps]
Error Message: [If any]
Browser Console Error: [Yes/No]
Severity: [Critical/High/Medium/Low]
Recommendation: [Fix needed]
```

---

## Performance Benchmarks

Expected response times:

| Operation | Expected Time | Max Acceptable |
|-----------|---------------|-----------------|
| Form load | < 1s | 2s |
| Evaluate click | 2-5s | 10s |
| Missing info submit | 2-5s | 10s |
| Debug output display | < 1s | 2s |

---

## Coverage Summary

| Category | Count | Status |
|----------|-------|--------|
| F1 Student | 6 | ✅ |
| H1B Work | 6 | ✅ |
| B1/B2 Visitor | 6 | ✅ |
| K1 Fiance | 6 | ✅ |
| Cross-cutting | 4 | ✅ |
| **Total Test Cases** | **28** | **✅** |

---

## How to Use This Document

1. **Manual Testing:** Follow each test case step-by-step in the Streamlit UI
2. **Regression Testing:** Run all 28 cases after code changes
3. **Quick Smoke Test:** Run XC tests + one case per visa type (6 cases total)
4. **Debugging:** Use specific test case when investigating issues
5. **Documentation:** Update with new edge cases discovered during testing
