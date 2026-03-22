"""
Quick test for Query 5 (H1B degree equivalency case)
"""
from inference_with_gemini import heuristic_assessment

# Query 5: H1B with degree equivalency (8 years exp + certifications, no bachelor's)
user_profile_q5 = {
    "age": "35",
    "nationality": "Philippines",
    "education": "High school diploma + IT certifications",
    "employment": "Systems Administrator",
    "income": "USD 65,000",
    "visa_type": "H1B",
    "extra": {
        "h1": {
            "job_offer": "Yes",
            "employer_name": "Accenture",
            "years_experience": "8",
            "degree_equiv": "Yes",
        }
    }
}

result = heuristic_assessment(user_profile_q5, [])
print("Query 5: H1B Degree Equivalency")
print(f"Decision: {result['decision']}")
print(f"Confidence: {result['confidence']}")
print(f"Explanation: {result['explanation']}")
print(f"Missing: {result.get('missing_information', [])}")
print()

# Expected: Likely Eligible (with 8 years exp + degree_equiv Yes + job offer)
if result['decision'] == "Likely Eligible" and result['confidence'] >= 70:
    print("✅ TEST PASSED - Query 5 returns correct decision")
else:
    print(f"❌ TEST FAILED - Expected 'Likely Eligible (70+)', got '{result['decision']} ({result['confidence']})'")
