from inference_with_gemini import run_rag_for_query
import time
import json
from datetime import datetime
import os

def test_visa(visa_type, user_profile, query):
    print(f"\n=== Testing {visa_type} Query ===")
    print("User Profile:", json.dumps(user_profile, indent=2))
    print("Query:", query)
    print("\nProcessing...")
    
    try:
        out = run_rag_for_query(user_profile, query)
        print("\nResults:")
        print("-" * 80)
        print("Decision:", out["decision"])
        print("Confidence:", out["confidence"])
        print("Explanation:", out["explanation"])
        print("Citations:", out["citations"])
        print("-" * 80)
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        # Log the test result
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "visa_type": visa_type,
            "profile": user_profile,
            "query": query,
            "decision": out["decision"],
            "confidence": out["confidence"],
            "explanation": out["explanation"],
            "citations": out["citations"]
        }
        with open("logs/visa_test_results.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        return True
    except Exception as e:
        print(f"\nError processing {visa_type}:")
        print(str(e))
        return False

def run_advanced_tests():
    print("Starting advanced visa eligibility tests...")
    print("=" * 80)
    
    test_cases = [
        # F1 Student Visa Cases
        {
            "name": "F1 Student Visa (Strong Case)",
            "profile": {
                "age": "22",
                "nationality": "India",
                "education": "Bachelor's in Progress",
                "employment": "Student",
                "income": "65000",
                "visa_type": "F1 Student",
                "additional_info": {
                    "university_acceptance": "Yes",
                    "english_proficiency": "IELTS 7.5",
                    "program": "Master's in Computer Science"
                }
            },
            "query": "F1 student visa requirements admission academic english proficiency financial documentation"
        },
        {
            "name": "F1 Student Visa (Weak Case)",
            "profile": {
                "age": "19",
                "nationality": "India",
                "education": "High School",
                "employment": "None",
                "income": "15000",
                "visa_type": "F1 Student",
                "additional_info": {
                    "university_acceptance": "No",
                    "english_proficiency": "None",
                    "program": "Undecided"
                }
            },
            "query": "F1 student visa requirements eligibility academic criteria financial support"
        },
        
        # B1/B2 Business Cases
        {
            "name": "B1/B2 Business Visa (Strong Case)",
            "profile": {
                "age": "45",
                "nationality": "India",
                "education": "Master's in Business",
                "employment": "CEO",
                "income": "150000",
                "visa_type": "B1/B2 Business",
                "additional_info": {
                    "company_revenue": "5000000",
                    "travel_purpose": "Business meetings",
                    "previous_travel": "Multiple"
                }
            },
            "query": "B1/B2 business visa requirements financial documentation business activities"
        },
        {
            "name": "B1/B2 Tourist Visa (Moderate Case)",
            "profile": {
                "age": "30",
                "nationality": "India",
                "education": "Bachelor's",
                "employment": "Software Engineer",
                "income": "45000",
                "visa_type": "B1/B2 Tourist",
                "additional_info": {
                    "travel_purpose": "Tourism",
                    "trip_duration": "2 weeks",
                    "hotel_bookings": "Yes"
                }
            },
            "query": "B1/B2 tourist visa requirements travel purpose accommodation proof funds"
        },
        
        # H1B Cases
        {
            "name": "H1B Work Visa (Strong Case)",
            "profile": {
                "age": "28",
                "nationality": "India",
                "education": "Master's in Computer Science",
                "employment": "Senior Software Engineer",
                "income": "130000",
                "visa_type": "H1B Work",
                "additional_info": {
                    "employer_sponsor": "Yes",
                    "job_offer": "Yes",
                    "experience": "5 years"
                }
            },
            "query": "H1B specialty occupation requirements education experience employer sponsorship"
        },
        {
            "name": "H1B Work Visa (Borderline Case)",
            "profile": {
                "age": "35",
                "nationality": "India",
                "education": "3-year Bachelor's",
                "employment": "IT Consultant",
                "income": "85000",
                "visa_type": "H1B Work",
                "additional_info": {
                    "employer_sponsor": "Yes",
                    "job_offer": "Yes",
                    "experience": "12 years"
                }
            },
            "query": "H1B visa requirements education equivalency experience evaluation"
        },
        
        # K1 Cases
        {
            "name": "K1 Fiancé Visa (Strong Case)",
            "profile": {
                "age": "27",
                "nationality": "India",
                "education": "Bachelor's",
                "employment": "Teacher",
                "income": "40000",
                "visa_type": "K1 Fiance",
                "additional_info": {
                    "met_in_person": "Yes",
                    "meeting_evidence": "Photos, tickets, hotel",
                    "relationship_length": "2 years",
                    "us_citizen_sponsor": "Yes"
                }
            },
            "query": "K1 fiance visa meeting requirement relationship evidence documentation"
        },
        {
            "name": "K1 Fiancé Visa (Complex Case)",
            "profile": {
                "age": "32",
                "nationality": "India",
                "education": "Master's",
                "employment": "Doctor",
                "income": "90000",
                "visa_type": "K1 Fiance",
                "additional_info": {
                    "met_in_person": "No",
                    "cultural_exception": "Yes",
                    "relationship_length": "1 year",
                    "us_citizen_sponsor": "Yes"
                }
            },
            "query": "K1 visa cultural exception meeting requirement relationship evidence"
        }
    ]
    
    success_count = 0
    for case in test_cases:
        print(f"\nExecuting test: {case['name']}")
        if test_visa(case['name'], case['profile'], case['query']):
            success_count += 1
        time.sleep(3)  # Add delay between tests to avoid rate limits
        
    print("\nTest Summary:")
    print(f"Completed {success_count} out of {len(test_cases)} tests successfully")
    print("\nDetailed results have been logged to logs/visa_test_results.jsonl")

if __name__ == "__main__":
    run_advanced_tests()