"""
Focused Test Suite for SwiftVisa - Testing Core Decision Logic
Tests key scenarios for each visa type to validate the system works correctly
"""

import json
import sys
import traceback
from unittest.mock import patch, MagicMock

# Ensure output uses UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from inference_with_gemini import run_rag_for_query, heuristic_assessment

def test_heuristic_directly():
    """Test the heuristic assessment function directly to ensure it works correctly"""
    print("\n" + "=" * 80)
    print("Testing Heuristic Assessment Function (Deterministic Logic)")
    print("=" * 80 + "\n")
    
    test_cases = [
        {
            "name": "F1 Complete - Eligible",
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
                        "i20_issued": "Yes",
                        "proof_of_funds_amount": "USD 100000"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "expected_has_missing": False
        },
        {
            "name": "F1 Missing I-20 - Ineligible",
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
                        "i20_issued": "No",
                        "proof_of_funds_amount": "USD 50000"
                    }
                }
            },
            "expected_decision": "Likely Ineligible",
            "expected_has_missing": False
        },
        {
            "name": "F1 Missing All Fields - Insufficient",
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
            "expected_has_missing": True
        },
        {
            "name": "H1B Complete with Job - Eligible",
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
            "expected_has_missing": False
        },
        {
            "name": "H1B No Job Offer - Ineligible",
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
            "expected_has_missing": False
        },
        {
            "name": "B1B2 with Return Ticket - Eligible",
            "profile": {
                "age": "45",
                "nationality": "India",
                "education": "Bachelors",
                "employment": "Business Owner",
                "income": "200000",
                "visa_type": "B1/B2 Visitor",
                "extra": {
                    "b1b2": {
                        "return_ticket": "Yes",
                        "travel_purpose": "Business",
                        "trip_duration_days": "10"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "expected_has_missing": False
        },
        {
            "name": "B1B2 Missing Return Ticket - Insufficient",
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
            "expected_has_missing": True
        },
        {
            "name": "K1 Complete Eligible",
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
            "expected_has_missing": False
        },
        {
            "name": "K1 Never Met - Ineligible",
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
            "expected_has_missing": False
        },
    ]
    
    passed = 0
    failed = 0
    
    for case in test_cases:
        result = heuristic_assessment(case["profile"], [])
        
        status = "✅ PASS"
        message = ""
        
        # Check decision
        if result["decision"] != case["expected_decision"]:
            status = "❌ FAIL"
            message += f"Decision: expected '{case['expected_decision']}', got '{result['decision']}'. "
            failed += 1
        else:
            passed += 1
        
        # Check missing info presence
        has_missing = len(result.get("missing_information", [])) > 0
        if has_missing != case["expected_has_missing"]:
            status = "❌ FAIL"
            message += f"Missing info: expected {case['expected_has_missing']}, got {has_missing}. "
            if passed > 0:
                passed -= 1
            failed += 1
        
        print(f"{status} {case['name']}")
        if message:
            print(f"   {message}")
        print(f"   Decision: {result['decision']} (Confidence: {result['confidence']})")
        if result.get("missing_information"):
            print(f"   Missing: {result['missing_information']}")
    
    print("\n" + "=" * 80)
    print(f"Heuristic Tests: {passed}/{len(test_cases)} PASSED")
    print("=" * 80)
    return passed == len(test_cases)


def test_with_rag_pipeline():
    """Test using the full RAG pipeline with mocked retrieve function"""
    print("\n" + "=" * 80)
    print("Testing RAG Pipeline with Mocked Retrieval")
    print("=" * 80 + "\n")
    
    test_cases = [
        {
            "name": "F1 Student - Complete Eligible",
            "visa_type": "F1 Student",
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
            "should_have_missing": False
        },
        {
            "name": "H1B Work - Strong Profile",
            "visa_type": "H1B Work",
            "profile": {
                "age": "32",
                "nationality": "India",
                "education": "Masters",
                "employment": "Software Engineer",
                "income": "250000",
                "visa_type": "H1B Work",
                "extra": {
                    "h1": {
                        "job_offer": "Yes",
                        "employer_name": "Google",
                        "years_experience": "8",
                        "degree_equiv": "Yes"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "should_have_missing": False
        },
        {
            "name": "B1B2 Visitor - Business Trip",
            "visa_type": "B1/B2 Visitor",
            "profile": {
                "age": "40",
                "nationality": "Japan",
                "education": "Masters",
                "employment": "Director",
                "income": "300000",
                "visa_type": "B1/B2 Visitor",
                "extra": {
                    "b1b2": {
                        "return_ticket": "Yes",
                        "travel_purpose": "business",
                        "trip_duration_days": "10",
                        "invitation_host": "XYZ Corp"
                    }
                }
            },
            "expected_decision": "Likely Eligible",
            "should_have_missing": False
        },
    ]
    
    passed = 0
    
    # Mock retrieve to avoid vectorstore loading
    with patch("inference_with_gemini.retrieve", return_value=[]):
        for case in test_cases:
            query = f"{case['visa_type']} requirements"
            result = run_rag_for_query(case["profile"], query)
            
            status = "✅ PASS" if result["decision"] == case["expected_decision"] else "❌ FAIL"
            
            # For eligible profiles, should not have missing info
            if "Likely Eligible" in result["decision"] and result["missing_information"]:
                status = "❌ FAIL"
            elif result["decision"] == case["expected_decision"]:
                passed += 1
            
            print(f"{status} {case['name']}")
            print(f"   Decision: {result['decision']} (Confidence: {result['confidence']})")
            if result.get("missing_information"):
                print(f"   Missing: {result['missing_information']}")
    
    print("\n" + "=" * 80)
    print(f"RAG Pipeline Tests: {passed}/{len(test_cases)} PASSED")
    print("=" * 80)
    return passed == len(test_cases)


if __name__ == "__main__":
    h_result = test_heuristic_directly()
    r_result = test_with_rag_pipeline()
    
    print("\n\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    print(f"Heuristic Tests: {'✅ PASSED' if h_result else '❌ FAILED'}")
    print(f"RAG Pipeline Tests: {'✅ PASSED' if r_result else '❌ FAILED'}")
    print("=" * 80 + "\n")
    
    exit(0 if (h_result and r_result) else 1)
