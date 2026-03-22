from inference_with_gemini import run_rag_for_query

def test_f1_visa():
    print("\n=== Testing F1 Student Visa Query ===")
    user = {
        "age": "22",
        "nationality": "India",
        "education": "High School",
        "employment": "Student",
        "income": "30000",
        "visa_type": "F1 Student"
    }
    query = "F1 student visa requirements eligibility criteria academic admission financial support"
    out = run_rag_for_query(user, query)
    print("Decision:", out["decision"])
    print("Confidence:", out["confidence"])
    print("Explanation:", out["explanation"])
    print("Citations:", out["citations"])

def test_b1b2_visa():
    print("\n=== Testing B1/B2 Business/Tourist Visa Query ===")
    user = {
        "age": "35",
        "nationality": "India",
        "education": "Bachelor's",
        "employment": "Business Owner",
        "income": "75000",
        "visa_type": "B1/B2 Visitor"
    }
    query = "B1/B2 visitor visa requirements eligibility criteria business tourist purpose financial documentation"
    out = run_rag_for_query(user, query)
    print("Decision:", out["decision"])
    print("Confidence:", out["confidence"])
    print("Explanation:", out["explanation"])
    print("Citations:", out["citations"])

def test_h1b_visa():
    print("\n=== Testing H1B Work Visa Query ===")
    user = {
        "age": "28",
        "nationality": "India",
        "education": "Master's in Computer Science",
        "employment": "Software Engineer",
        "income": "120000",
        "visa_type": "H1B Work"
    }
    query = "H1B work visa requirements eligibility criteria specialty occupation education experience"
    out = run_rag_for_query(user, query)
    print("Decision:", out["decision"])
    print("Confidence:", out["confidence"])
    print("Explanation:", out["explanation"])
    print("Citations:", out["citations"])

if __name__ == "__main__":
    print("Running visa eligibility tests...")
    
    test_f1_visa()
    test_b1b2_visa()
    test_h1b_visa()