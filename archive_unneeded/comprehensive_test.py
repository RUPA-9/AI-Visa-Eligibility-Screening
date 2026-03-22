from inference_with_gemini import run_rag_for_query

def test_visa(visa_type, user_profile, query):
    print(f"\n=== Testing {visa_type} Query ===")
    out = run_rag_for_query(user_profile, query)
    print("Decision:", out["decision"])
    print("Confidence:", out["confidence"])
    print("Explanation:", out["explanation"])
    print("Citations:", out["citations"])

if __name__ == "__main__":
    print("Running comprehensive visa eligibility tests...")
    
    # Test Case 1: F1 Student Visa
    test_visa(
        "F1 Student Visa",
        {
            "age": "22",
            "nationality": "India",
            "education": "Bachelor's in Progress",
            "employment": "Student",
            "income": "30000",
            "visa_type": "F1 Student"
        },
        "F1 student visa requirements eligibility criteria academic admission financial support I-20 SEVIS"
    )
    
    # Test Case 2: B1/B2 Business/Tourist Visa
    test_visa(
        "B1/B2 Business/Tourist Visa",
        {
            "age": "35",
            "nationality": "India",
            "education": "Bachelor's",
            "employment": "Business Owner",
            "income": "75000",
            "visa_type": "B1/B2 Visitor"
        },
        "B1/B2 visitor visa requirements eligibility criteria business tourist purpose financial documentation"
    )
    
    # Test Case 3: H1B Work Visa
    test_visa(
        "H1B Work Visa",
        {
            "age": "28",
            "nationality": "India",
            "education": "Master's in Computer Science",
            "employment": "Software Engineer",
            "income": "120000",
            "visa_type": "H1B Work"
        },
        "H1B work visa requirements eligibility criteria specialty occupation education experience employer sponsorship"
    )
    
    # Test Case 4: K1 Fiancé Visa
    test_visa(
        "K1 Fiancé Visa",
        {
            "age": "27",
            "nationality": "India",
            "education": "Bachelor's",
            "employment": "Teacher",
            "income": "45000",
            "visa_type": "K1 Fiance"
        },
        "K1 fiance visa requirements eligibility criteria relationship evidence meeting requirement financial support"
    )
    
    # Test Case 5: B1/B2 Tourist Visa (Lower Income)
    test_visa(
        "B1/B2 Tourist Visa (Lower Income)",
        {
            "age": "45",
            "nationality": "India",
            "education": "High School",
            "employment": "Self Employed",
            "income": "25000",
            "visa_type": "B1/B2 Visitor"
        },
        "B1/B2 tourist visa requirements eligibility criteria travel purpose financial documentation proof of ties"
    )