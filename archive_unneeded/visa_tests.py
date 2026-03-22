from inference_with_gemini import run_rag_for_query
import time

def test_visa(visa_type, user_profile, query):
    print(f"\n=== Testing {visa_type} Query ===")
    print("User Profile:", user_profile)
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
        return True
    except Exception as e:
        print(f"\nError processing {visa_type}:")
        print(str(e))
        return False

def run_tests():
    print("Starting visa eligibility tests...")
    print("=" * 80)
    
    test_cases = [
        # Test Case 1: F1 Student with Admission
        {
            "name": "F1 Student Visa (With Admission)",
            "profile": {
                "age": "22",
                "nationality": "India",
                "education": "Bachelor's in Progress",
                "employment": "Student",
                "income": "35000",
                "visa_type": "F1 Student"
            },
            "query": "F1 student visa requirements eligibility criteria academic admission financial support I-20 SEVIS"
        },
        
        # Test Case 2: B1/B2 Business Visitor
        {
            "name": "B1/B2 Business Visa",
            "profile": {
                "age": "35",
                "nationality": "India",
                "education": "Master's",
                "employment": "Business Owner",
                "income": "85000",
                "visa_type": "B1/B2 Visitor"
            },
            "query": "B1/B2 business visa requirements eligibility criteria business activities financial documentation"
        },
        
        # Test Case 3: K1 Fiancé
        {
            "name": "K1 Fiancé Visa",
            "profile": {
                "age": "28",
                "nationality": "India",
                "education": "Bachelor's",
                "employment": "Software Engineer",
                "income": "65000",
                "visa_type": "K1 Fiance"
            },
            "query": "K1 fiance visa requirements eligibility criteria relationship proof financial support marriage intent"
        }
    ]
    
    success_count = 0
    for case in test_cases:
        print(f"\nExecuting test: {case['name']}")
        if test_visa(case['name'], case['profile'], case['query']):
            success_count += 1
        time.sleep(2)  # Add delay between tests to avoid rate limits
        
    print("\nTest Summary:")
    print(f"Completed {success_count} out of {len(test_cases)} tests successfully")

if __name__ == "__main__":
    run_tests()