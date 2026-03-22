"""
Batch test for Queries 7, 9-15 using the heuristic assessment function
"""
from inference_with_gemini import heuristic_assessment

# Define all test queries with their profiles
test_cases = {
    "Query 7: B1/B2 Strong Ties (Business)": {
        "profile": {
            "age": "45",
            "nationality": "India",
            "education": "MBA",
            "employment": "CEO - Manufacturing Company",
            "income": "INR 3,000,000 per year",
            "visa_type": "B1/B2",
            "extra": {
                "b1b2": {
                    "travel_purpose": "business",
                    "trip_duration_days": "14",
                    "invitation_host": "Supplier ABC Corporation California",
                    "return_ticket": "Yes",
                }
            }
        },
        "expected": "Likely Eligible (75+)"
    },
    "Query 9: B1/B2 Weak Ties (Tourist)": {
        "profile": {
            "age": "35",
            "nationality": "Pakistan",
            "education": "High school",
            "employment": "Unemployed",
            "income": "No current income",
            "visa_type": "B1/B2",
            "extra": {
                "b1b2": {
                    "travel_purpose": "tourism",
                    "trip_duration_days": "30",
                    "invitation_host": "Cousin in Los Angeles",
                    "return_ticket": "No",
                }
            }
        },
        "expected": "Insufficient Data / Ineligible"
    },
    "Query 10: K1 Complete Eligible": {
        "profile": {
            "age": "29",
            "nationality": "Philippines",
            "education": "Bachelor's in Business",
            "employment": "Marketing Specialist",
            "income": "PHP 500,000 per year",
            "visa_type": "K1",
            "extra": {
                "k1": {
                    "us_citizen_sponsor": "Yes",
                    "met_in_person": "Yes",
                    "relationship_length_months": "18",
                    "evidence_list": "Engagement photos, flight tickets, visa stamps, WhatsApp messages",
                }
            }
        },
        "expected": "Likely Eligible (75+)"
    },
    "Query 11: K1 Recent Relationship (2 months)": {
        "profile": {
            "age": "26",
            "nationality": "Mexico",
            "education": "Associate's degree",
            "employment": "Teacher",
            "income": "MXN 250,000 per year",
            "visa_type": "K1",
            "extra": {
                "k1": {
                    "us_citizen_sponsor": "Yes",
                    "met_in_person": "Yes",
                    "relationship_length_months": "2",
                    "evidence_list": "Photos from trip to Mexico, travel documents",
                }
            }
        },
        "expected": "Likely Eligible (65+)"
    },
    "Query 12: K1 No In-Person Meeting": {
        "profile": {
            "age": "32",
            "nationality": "Bangladesh",
            "education": "Bachelor's in Engineering",
            "employment": "Software Developer",
            "income": "BDT 800,000 per year",
            "visa_type": "K1",
            "extra": {
                "k1": {
                    "us_citizen_sponsor": "Yes",
                    "met_in_person": "No",
                    "relationship_length_months": "12",
                    "evidence_list": "Video call screenshots, online chat logs, social media proof",
                }
            }
        },
        "expected": "Likely Ineligible (35-40)"
    },
    "Query 13: Multiple Visa Options (H1B vs K1)": {
        "profile": {
            "age": "27",
            "nationality": "India",
            "education": "Master's in Computer Science",
            "employment": "Software Engineer",
            "income": "USD 80,000 (proposed salary)",
            "visa_type": "H1B",
            "extra": {
                "h1": {
                    "job_offer": "Yes",
                    "employer_name": "US Tech Company",
                    "years_experience": "3",
                    "degree_equiv": "Yes",
                }
            }
        },
        "expected": "Likely Eligible (70+) for H1B"
    },
    "Query 14: Status Change (B1 to H1B)": {
        "profile": {
            "age": "30",
            "nationality": "Canada",
            "education": "Bachelor's in IT",
            "employment": "Currently on B-1 business visit",
            "income": "USD 95,000 (from new job offer)",
            "visa_type": "H1B",
            "extra": {
                "h1": {
                    "job_offer": "Yes",
                    "employer_name": "Tech Company",
                    "years_experience": "6",
                    "degree_equiv": "Yes",
                }
            }
        },
        "expected": "Likely Eligible (70+)"
    },
    "Query 15: F1 Post-Graduation OPT": {
        "profile": {
            "age": "25",
            "nationality": "Taiwan",
            "education": "Master's in Data Science (graduating December 2025)",
            "employment": "Graduate Student",
            "income": "No personal income (teaching assistant stipend)",
            "visa_type": "F1",
            "extra": {
                "f1": {
                    "university_acceptance": "Yes",
                    "school_name": "University of Washington",
                    "i20_issued": "Yes",
                    "proof_of_funds_amount": "USD 40,000",
                    "test_scores": "TOEFL 100",
                }
            }
        },
        "expected": "Likely Eligible (75+)"
    },
}

# Run all tests
print("=" * 80)
print("TESTING QUERIES 7, 9-15")
print("=" * 80)
print()

results = []
for test_name, test_data in test_cases.items():
    profile = test_data["profile"]
    expected = test_data["expected"]
    
    result = heuristic_assessment(profile, [])
    
    decision = result['decision']
    confidence = result['confidence']
    explanation = result['explanation']
    missing = result.get('missing_information', [])
    
    results.append({
        "name": test_name,
        "decision": decision,
        "confidence": confidence,
        "expected": expected,
        "explanation": explanation,
        "missing": missing
    })
    
    print(f"{'='*80}")
    print(f"{test_name}")
    print(f"{'='*80}")
    print(f"Decision: {decision}")
    print(f"Confidence: {confidence}")
    print(f"Expected: {expected}")
    print(f"Explanation: {explanation}")
    if missing:
        print(f"Missing Information: {missing}")
    print()

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
for r in results:
    status = "✅ LIKELY CORRECT" if r["confidence"] > 0 else "❌ CHECK"
    print(f"{r['name']}: {r['decision']} ({r['confidence']}) {status}")
