"""
Debug script to see what the LLM is actually returning
"""

from unittest.mock import patch
from inference_with_gemini import run_rag_for_query

# Test case
profile = {
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
}

query = "F1 Student requirements"

# Mock retrieve to avoid vectorstore loading
with patch("inference_with_gemini.retrieve", return_value=[]):
    result = run_rag_for_query(profile, query)
    
print("FULL RESULT:")
print("=" * 80)
for key, value in result.items():
    if key != "user_profile":
        print(f"{key}: {value}")

print("\n" + "=" * 80)
print("RAW OUTPUT:")
print("=" * 80)
print(result.get("raw_output", "No raw output"))
