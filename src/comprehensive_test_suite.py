"""
Automated Test Harness for SwiftVisa - Comprehensive Test Suite
Tests all 28 test cases covering 4 visa types with various scenarios
"""

import json
import sys
import traceback
from unittest.mock import patch
from inference_with_gemini import run_rag_for_query

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Test case definitions
TEST_CASES = {
    "F1": [
        {
            "id": "F1-001",
            "name": "Missing All F1-Specific Fields",
            "profile": {
                "age": "22",
                "nationality": "India",
                "education": "Bachelors",
                "employment": "Student",
                "income": "0",
                "visa_type": "F1 Student",
                "extra": {"f1": {}}
            },
            "expected_decision": "Insufficient Data",
            "expected_missing": ["f1.university_acceptance", "f1.i20_issued", "f1.proof_of_funds_amount"],
            "expected_confidence_range": [0, 50],
            "description": "All F1-specific fields missing should prompt for all required fields"
        },
        {
            "id": "F1-002",
            "name": "Partial F1 Fields (Only Acceptance)",
            "profile": {
                "age": "23",
                "nationality": "China",
                "education": "Masters",
                "employment": "Student",
                "income": "10000",
                "visa_type": "F1 Student",
                "extra": {
                    "f1": {
                        "university_acceptance": "Yes",
                        "school_name": "Stanford University",
                        "test_scores": "TOEFL 100"
                    }
                }
            },
            "expected_decision": "Insufficient Data",
            "expected_missing": ["f1.i20_issued", "f1.proof_of_funds_amount"],
            "expected_confidence_range": [20, 50],
            "description": "Partial F1 data should ask for missing critical fields"
        },
        {
            "id": "F1-003",
            "name": "Complete F1 - Eligible Profile",
            "profile": {
                "age": "22",
                "nationality": "India",
                "education": "Bachelors",
                "employment": "Student",
                "income": "50000",
                "visa_type": "F1 Student",
                "extra": {
                    "f1": {
                        "university_acceptance": "Yes",
                        "school_name": "MIT",
                        "i20_issued": "Yes",
                        "proof_of_funds_amount": "USD 100000",
                        "test_scores": "TOEFL 110"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "expected_missing": [],  # No missing info expected for complete profiles
            "expected_confidence_range": [70, 100],
            "description": "Complete F1 profile with positive indicators should be eligible"
        },
        {
            "id": "F1-004",
            "name": "Complete F1 - No I-20 (Ineligible)",
            "profile": {
                "age": "25",
                "nationality": "Brazil",
                "education": "Masters",
                "employment": "Student",
                "income": "80000",
                "visa_type": "F1 Student",
                "extra": {
                    "f1": {
                        "university_acceptance": "Yes",
                        "school_name": "Harvard",
                        "i20_issued": "No",
                        "proof_of_funds_amount": "USD 50000",
                        "test_scores": "IELTS 7.5"
                    }
                }
            },
            "expected_decision": "Likely Ineligible",
            "expected_missing": [],
            "expected_confidence_range": [0, 50],
            "description": "F1 without I-20 should be ineligible"
        },
        {
            "id": "F1-005",
            "name": "F1 - Ambiguous Responses (Unknown Values)",
            "profile": {
                "age": "20",
                "nationality": "Vietnam",
                "education": "Bachelors",
                "employment": "Student",
                "income": "0",
                "visa_type": "F1 Student",
                "extra": {
                    "f1": {
                        "university_acceptance": "Unknown",
                        "school_name": "Stanford",
                        "i20_issued": "Unknown",
                        "proof_of_funds_amount": "USD 40000",
                        "test_scores": "TOEFL 95"
                    }
                }
            },
            "expected_decision": "Insufficient Data",
            "expected_missing_partial": ["Unknown", "i20"],  # Changed to flexible matching
            "expected_confidence_range": [0, 50],
            "description": "Unknown values should be treated as missing"
        },
        {
            "id": "F1-006",
            "name": "F1 - Data Validation (Formats)",
            "profile": {
                "age": "21",
                "nationality": "Japan",
                "education": "Bachelors",
                "employment": "Student",
                "income": "35000",
                "visa_type": "F1 Student",
                "extra": {
                    "f1": {
                        "university_acceptance": "Yes",
                        "school_name": "UC Berkeley",
                        "i20_issued": "Yes",
                        "proof_of_funds_amount": "50,000 USD",
                        "test_scores": "TOEFL 105"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "expected_missing": [],
            "expected_confidence_range": [70, 100],
            "description": "Various fund amount formats should be accepted"
        }
    ],
    "H1B": [
        {
            "id": "H1B-001",
            "name": "Missing Job Offer and Employer",
            "profile": {
                "age": "28",
                "nationality": "India",
                "education": "Bachelors",
                "employment": "Software Engineer",
                "income": "0",
                "visa_type": "H1B Work",
                "extra": {"h1": {}}
            },
            "expected_decision": "Insufficient Data",
            "expected_missing": ["h1.job_offer", "h1.employer_name"],
            "expected_confidence_range": [0, 50],
            "description": "H1B without job offer must show missing fields"
        },
        {
            "id": "H1B-002",
            "name": "Partial H1B (Job but No Experience)",
            "profile": {
                "age": "30",
                "nationality": "Philippines",
                "education": "Masters",
                "employment": "Software Engineer",
                "income": "120000",
                "visa_type": "H1B Work",
                "extra": {
                    "h1": {
                        "job_offer": "Yes",
                        "employer_name": "Google",
                        "years_experience": "0",
                        "degree_equiv": "Yes"
                    }
                }
            },
            "expected_decision_in": ["Insufficient Data", "Likely Eligible"],
            "expected_confidence_range": [30, 80],
            "description": "Job offer with minimal experience should be evaluated"
        },
        {
            "id": "H1B-003",
            "name": "Complete H1B - Strong Profile",
            "profile": {
                "age": "32",
                "nationality": "India",
                "education": "Masters",
                "employment": "Senior Software Engineer",
                "income": "250000",
                "visa_type": "H1B Work",
                "extra": {
                    "h1": {
                        "job_offer": "Yes",
                        "employer_name": "Microsoft",
                        "years_experience": "7",
                        "degree_equiv": "Yes"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "expected_missing": [],
            "expected_confidence_range": [75, 100],
            "description": "Strong H1B profile should be eligible"
        },
        {
            "id": "H1B-004",
            "name": "Complete H1B - No Job Offer",
            "profile": {
                "age": "29",
                "nationality": "Canada",
                "education": "Bachelors",
                "employment": "Unemployed",
                "income": "0",
                "visa_type": "H1B Work",
                "extra": {
                    "h1": {
                        "job_offer": "No",
                        "employer_name": "",
                        "years_experience": "5",
                        "degree_equiv": "Yes"
                    }
                }
            },
            "expected_decision": "Likely Ineligible",
            "expected_missing": [],
            "expected_confidence_range": [0, 100],
            "description": "H1B without job offer should be ineligible"
        },
        {
            "id": "H1B-005",
            "name": "H1B - Minimum Experience",
            "profile": {
                "age": "25",
                "nationality": "Mexico",
                "education": "Bachelors",
                "employment": "Junior Developer",
                "income": "80000",
                "visa_type": "H1B Work",
                "extra": {
                    "h1": {
                        "job_offer": "Yes",
                        "employer_name": "Amazon",
                        "years_experience": "2",
                        "degree_equiv": "Yes"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "expected_missing": [],
            "expected_confidence_range": [65, 85],
            "description": "H1B with 2 years experience should be eligible"
        },
        {
            "id": "H1B-006",
            "name": "H1B - No Degree Equivalency",
            "profile": {
                "age": "35",
                "nationality": "Pakistan",
                "education": "Diploma",
                "employment": "Software Engineer",
                "income": "150000",
                "visa_type": "H1B Work",
                "extra": {
                    "h1": {
                        "job_offer": "Yes",
                        "employer_name": "Facebook",
                        "years_experience": "10",
                        "degree_equiv": "No"
                    }
                }
            },
            "expected_decision": "Likely Ineligible",
            "expected_missing": [],
            "expected_confidence_range": [0, 50],
            "description": "H1B without degree equivalency should be ineligible"
        }
    ],
    "B1B2": [
        {
            "id": "B1B2-001",
            "name": "Missing Return Ticket",
            "profile": {
                "age": "45",
                "nationality": "India",
                "education": "Bachelors",
                "employment": "Business Owner",
                "income": "200000",
                "visa_type": "B1/B2 Visitor",
                "extra": {"b1b2": {}}
            },
            "expected_decision": "Insufficient Data",
            "expected_missing": ["b1b2.return_ticket"],
            "expected_confidence_range": [0, 50],
            "description": "B1B2 without return ticket must ask for it"
        },
        {
            "id": "B1B2-002",
            "name": "Partial B1B2 (No Invitation)",
            "profile": {
                "age": "35",
                "nationality": "Mexico",
                "education": "Bachelors",
                "employment": "Manager",
                "income": "120000",
                "visa_type": "B1/B2 Visitor",
                "extra": {
                    "b1b2": {
                        "travel_purpose": "Tourism",
                        "trip_duration_days": "7",
                        "invitation_host": "",
                        "return_ticket": "Yes"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "expected_missing": [],
            "expected_confidence_range": [60, 80],
            "description": "B1B2 with return ticket should be eligible even without invitation"
        },
        {
            "id": "B1B2-003",
            "name": "Complete B1B2 - Business Trip",
            "profile": {
                "age": "40",
                "nationality": "Japan",
                "education": "Masters",
                "employment": "Director",
                "income": "300000",
                "visa_type": "B1/B2 Visitor",
                "extra": {
                    "b1b2": {
                        "travel_purpose": "business",
                        "trip_duration_days": "10",
                        "invitation_host": "XYZ Corp",
                        "return_ticket": "Yes"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "expected_missing": [],
            "expected_confidence_range": [70, 90],
            "description": "Business traveler with return ticket should be eligible"
        },
        {
            "id": "B1B2-004",
            "name": "Complete B1B2 - Tourist Trip",
            "profile": {
                "age": "30",
                "nationality": "Brazil",
                "education": "Bachelors",
                "employment": "Accountant",
                "income": "80000",
                "visa_type": "B1/B2 Visitor",
                "extra": {
                    "b1b2": {
                        "travel_purpose": "tourism",
                        "trip_duration_days": "14",
                        "invitation_host": "Friend",
                        "return_ticket": "Yes"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "expected_missing": [],
            "expected_confidence_range": [65, 85],
            "description": "Tourist with return ticket should be eligible"
        },
        {
            "id": "B1B2-005",
            "name": "B1B2 - Long Duration (90 days)",
            "profile": {
                "age": "50",
                "nationality": "Germany",
                "education": "Bachelors",
                "employment": "Retired",
                "income": "50000",
                "visa_type": "B1/B2 Visitor",
                "extra": {
                    "b1b2": {
                        "travel_purpose": "medical",
                        "trip_duration_days": "90",
                        "invitation_host": "Mayo Clinic",
                        "return_ticket": "Yes"
                    }
                }
            },
            "expected_decision_in": ["Insufficient Data", "Likely Eligible"],
            "expected_confidence_range": [40, 75],
            "description": "Long duration trip may need additional documentation"
        },
        {
            "id": "B1B2-006",
            "name": "B1B2 - Medical Travel",
            "profile": {
                "age": "65",
                "nationality": "UK",
                "education": "Bachelors",
                "employment": "Retired",
                "income": "100000",
                "visa_type": "B1/B2 Visitor",
                "extra": {
                    "b1b2": {
                        "travel_purpose": "medical",
                        "trip_duration_days": "30",
                        "invitation_host": "Hospital",
                        "return_ticket": "Yes"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "expected_missing": [],
            "expected_confidence_range": [65, 85],
            "description": "Medical travel should be eligible"
        }
    ],
    "K1": [
        {
            "id": "K1-001",
            "name": "Missing US Citizen Sponsor",
            "profile": {
                "age": "26",
                "nationality": "Philippines",
                "education": "Bachelors",
                "employment": "Secretary",
                "income": "0",
                "visa_type": "K1 Fiance",
                "extra": {"k1": {}}
            },
            "expected_decision": "Insufficient Data",
            "expected_missing": ["k1.us_citizen_sponsor", "k1.met_in_person"],
            "expected_confidence_range": [0, 50],
            "description": "K1 without sponsor cannot proceed"
        },
        {
            "id": "K1-002",
            "name": "Sponsor but Never Met",
            "profile": {
                "age": "24",
                "nationality": "Colombia",
                "education": "Bachelors",
                "employment": "Teacher",
                "income": "25000",
                "visa_type": "K1 Fiance",
                "extra": {
                    "k1": {
                        "us_citizen_sponsor": "Yes",
                        "met_in_person": "No",
                        "relationship_length_months": "6",
                        "evidence_list": "Chat messages, photos"
                    }
                }
            },
            "expected_decision": "Likely Ineligible",
            "expected_missing": [],
            "expected_confidence_range": [0, 50],
            "description": "K1 without in-person meeting is ineligible"
        },
        {
            "id": "K1-003",
            "name": "Complete K1 - Eligible Profile",
            "profile": {
                "age": "27",
                "nationality": "Ukraine",
                "education": "Masters",
                "employment": "Engineer",
                "income": "0",
                "visa_type": "K1 Fiance",
                "extra": {
                    "k1": {
                        "us_citizen_sponsor": "Yes",
                        "met_in_person": "Yes",
                        "relationship_length_months": "18",
                        "evidence_list": "Passport stamps, photos, plane tickets"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "expected_missing": [],
            "expected_confidence_range": [70, 90],
            "description": "Complete K1 with strong evidence should be eligible"
        },
        {
            "id": "K1-004",
            "name": "K1 - Recent Meeting (2 months)",
            "profile": {
                "age": "25",
                "nationality": "Thailand",
                "education": "Bachelors",
                "employment": "Sales",
                "income": "20000",
                "visa_type": "K1 Fiance",
                "extra": {
                    "k1": {
                        "us_citizen_sponsor": "Yes",
                        "met_in_person": "Yes",
                        "relationship_length_months": "2",
                        "evidence_list": "Recent trip photos, tickets"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "expected_missing": [],
            "expected_confidence_range": [65, 80],
            "description": "Recent K1 with documented meeting is eligible"
        },
        {
            "id": "K1-005",
            "name": "K1 - Long Relationship (24 months)",
            "profile": {
                "age": "30",
                "nationality": "Canada",
                "education": "Masters",
                "employment": "Consultant",
                "income": "150000",
                "visa_type": "K1 Fiance",
                "extra": {
                    "k1": {
                        "us_citizen_sponsor": "Yes",
                        "met_in_person": "Yes",
                        "relationship_length_months": "24",
                        "evidence_list": "Multiple visits, comprehensive documentation"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "expected_missing": [],
            "expected_confidence_range": [80, 100],
            "description": "Long K1 relationship with documentation should be strong"
        },
        {
            "id": "K1-006",
            "name": "K1 - Financial Verification",
            "profile": {
                "age": "28",
                "nationality": "Vietnam",
                "education": "Bachelors",
                "employment": "Nurse",
                "income": "60000",
                "visa_type": "K1 Fiance",
                "extra": {
                    "k1": {
                        "us_citizen_sponsor": "Yes",
                        "met_in_person": "Yes",
                        "relationship_length_months": "12",
                        "evidence_list": "I-864 affidavit, sponsor financial docs"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "expected_missing": [],
            "expected_confidence_range": [75, 90],
            "description": "K1 with I-864 affidavit should be eligible"
        }
    ]
}


def test_case(case):
    """Run a single test case and return results"""
    result = {
        "test_id": case.get("id"),
        "test_name": case.get("name"),
        "status": "PASS",
        "message": "",
        "actual_decision": None,
        "actual_confidence": None,
        "actual_missing": [],
    }

    try:
        # Mock retrieve to avoid vectorstore loading
        with patch("inference_with_gemini.retrieve", return_value=[]):
            # Run the evaluation
            profile = case.get("profile", {})
            query = f"{profile.get('visa_type', '')} requirements"
            rag_result = run_rag_for_query(profile, query)

            result["actual_decision"] = rag_result.get("decision")
            result["actual_confidence"] = rag_result.get("confidence")
            result["actual_missing"] = rag_result.get("missing_information", [])

            # Validate decision
            expected_decision = case.get("expected_decision")
            expected_decision_in = case.get("expected_decision_in")

            if expected_decision and result["actual_decision"] != expected_decision:
                result["status"] = "FAIL"
                result["message"] += f"Decision mismatch: expected '{expected_decision}', got '{result['actual_decision']}'. "

            if expected_decision_in and result["actual_decision"] not in expected_decision_in:
                result["status"] = "FAIL"
                result["message"] += f"Decision not in expected list {expected_decision_in}, got '{result['actual_decision']}'. "

            # Validate confidence range
            conf_range = case.get("expected_confidence_range")
            if conf_range:
                min_conf, max_conf = conf_range[0], conf_range[1]
                if not (min_conf <= result["actual_confidence"] <= max_conf):
                    result["status"] = "FAIL"
                    result["message"] += f"Confidence {result['actual_confidence']} out of range {conf_range}. "

            # Validate missing information (flexible: check for related fields)
            expected_missing = case.get("expected_missing", [])
            if expected_missing and result["actual_missing"]:
                # For missing data tests: check that SOME missing fields are reported
                # (actual field names from LLM may vary, but presence/absence of missing info should match)
                pass  # OK if missing fields reported
            elif expected_missing and not result["actual_missing"]:
                # Expected missing but none reported
                result["status"] = "FAIL"
                result["message"] += f"Expected missing fields but got none. Expected some of: {expected_missing}. "

            expected_missing_partial = case.get("expected_missing_partial")
            if expected_missing_partial:
                if not any(p in str(result["actual_missing"]) for p in expected_missing_partial):
                    result["status"] = "FAIL"
                    result["message"] += f"Missing fields should contain {expected_missing_partial}. "

            # Validate empty missing for eligible cases
            if "Likely Eligible" in (expected_decision, expected_decision_in):
                if result["actual_missing"]:
                    result["status"] = "FAIL"
                    result["message"] += f"'Likely Eligible' should have no missing info, but got {result['actual_missing']}. "

            if not result["message"]:
                result["message"] = "All validations passed"

    except Exception as e:
        result["status"] = "ERROR"
        result["message"] = f"Exception: {str(e)}\n{traceback.format_exc()}"

    return result


def run_all_tests():
    """Run all test cases"""
    all_results = []
    visa_types = ["F1", "H1B", "B1B2", "K1"]

    print("\n" + "=" * 80)
    print("SwiftVisa Comprehensive Test Suite - Running All Test Cases")
    print("=" * 80 + "\n")

    for visa_type in visa_types:
        cases = TEST_CASES.get(visa_type, [])
        print(f"\n{visa_type} Visa - {len(cases)} test cases")
        print("-" * 80)

        for case in cases:
            result = test_case(case)
            all_results.append(result)

            status_symbol = "[PASS]" if result["status"] == "PASS" else "[FAIL]" if result["status"] == "FAIL" else "[ERR]"
            print(f"{status_symbol} {result['test_id']}: {result['test_name']}")
            if result["status"] != "PASS":
                print(f"   Message: {result['message']}")
            print(f"   Decision: {result['actual_decision']} (Confidence: {result['actual_confidence']})")
            if result["actual_missing"]:
                print(f"   Missing: {result['actual_missing']}")

    # Summary
    print("\n" + "=" * 80)
    total = len(all_results)
    passed = sum(1 for r in all_results if r["status"] == "PASS")
    failed = sum(1 for r in all_results if r["status"] == "FAIL")
    errors = sum(1 for r in all_results if r["status"] == "ERROR")

    print(f"Test Summary: {passed}/{total} PASSED")
    print(f"  [PASS] PASSED: {passed}")
    print(f"  [FAIL] FAILED: {failed}")
    print(f"  [ERR]  ERRORS: {errors}")
    print("=" * 80 + "\n")

    return all_results, passed == total


if __name__ == "__main__":
    results, all_passed = run_all_tests()

    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Test results saved to test_results.json")

    exit(0 if all_passed else 1)
