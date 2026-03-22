import streamlit as st
from typing import Dict, Any, List

# We call the existing RAG/evaluation function. It is expected to return a dict
# that may include a `missing_information` key with a list of missing field names
# when more input is required.
from inference_with_gemini import run_rag_for_query

# NOTE: we request the extra fields below because they map directly to the
# eligibility criteria that consular officers typically use to decide visa
# applications (admission/I-20 for students, employer/job offer for work visas,
# trip purpose and return evidence for visitor visas, meeting/evidence for K1
# fiance visas). Collecting these minimal structured fields makes it easy to
# decide or to surface exactly which pieces of information are still missing.


def get_category(visa_type: str) -> str:
    vt = visa_type.lower() if visa_type else ""
    if "f1" in vt or "student" in vt:
        return "f1"
    if "h1" in vt or "work" in vt:
        return "h1"
    if "b1" in vt or "b2" in vt or "tourist" in vt:
        return "b1b2"
    if "k1" in vt or "fiance" in vt or "fianc" in vt:
        return "k1"
    return "other"


def render_visa_specific_inputs(category: str, extra: Dict[str, Any]):
    """Render visa-specific inputs and write values into extra[category]."""
    if category not in extra:
        extra[category] = {}

    if category == "f1":
        # safer default index selection
        ua_default = extra[category].get("university_acceptance", "Unknown")
        try:
            ua_index = ["Yes", "No", "Unknown"].index(ua_default)
        except ValueError:
            ua_index = 2
        extra[category]["university_acceptance"] = st.selectbox(
            "University acceptance?", ["Yes", "No", "Unknown"], index=ua_index
        )
        extra[category]["school_name"] = st.text_input(
            "School / University name", value=extra[category].get("school_name", "")
        )
        i20_default = extra[category].get("i20_issued", "Unknown")
        try:
            i20_index = ["Yes", "No", "Unknown"].index(i20_default)
        except ValueError:
            i20_index = 2
        extra[category]["i20_issued"] = st.selectbox(
            "Is Form I-20 issued?", ["Yes", "No", "Unknown"], index=i20_index
        )
        extra[category]["proof_of_funds_amount"] = st.text_input(
            "Proof of funds amount (currency & amount)", value=extra[category].get("proof_of_funds_amount", "")
        )
        extra[category]["test_scores"] = st.text_input(
            "Test scores (TOEFL/IELTS/etc)", value=extra[category].get("test_scores", "")
        )

    elif category == "h1":
        job_default = extra[category].get("job_offer", "No")
        try:
            job_index = ["Yes", "No"].index(job_default)
        except ValueError:
            job_index = 1
        extra[category]["job_offer"] = st.selectbox(
            "Job offer available?", ["Yes", "No"], index=job_index
        )
        extra[category]["employer_name"] = st.text_input(
            "Employer name", value=extra[category].get("employer_name", "")
        )
        extra[category]["years_experience"] = st.number_input(
            "Years of experience", value=int(extra[category].get("years_experience", 0)), min_value=0, step=1
        )
        extra[category]["degree_equiv"] = st.selectbox(
            "Degree equivalency to US bachelor's?", ["Yes", "No", "Unknown"], index=2 if extra[category].get("degree_equiv") is None else ["Yes","No","Unknown"].index(extra[category].get("degree_equiv", "Unknown"))
        )

    elif category == "b1b2":
        tp_default = extra[category].get("travel_purpose", "tourism")
        try:
            tp_index = ["business", "tourism", "medical"].index(tp_default)
        except ValueError:
            tp_index = 1
        extra[category]["travel_purpose"] = st.selectbox(
            "Travel purpose", ["business", "tourism", "medical"], index=tp_index
        )
        extra[category]["trip_duration_days"] = st.number_input(
            "Trip duration (days)", value=int(extra[category].get("trip_duration_days", 7)), min_value=1, step=1
        )
        extra[category]["invitation_host"] = st.text_input(
            "Invitation / host (if any)", value=extra[category].get("invitation_host", "")
        )
        rt_default = extra[category].get("return_ticket", "No")
        try:
            rt_index = ["Yes", "No"].index(rt_default)
        except ValueError:
            rt_index = 1
        extra[category]["return_ticket"] = st.selectbox(
            "Return ticket booked?", ["Yes", "No"], index=rt_index
        )

    elif category == "k1":
        sponsor_default = extra[category].get("us_citizen_sponsor", "No")
        try:
            sponsor_index = ["Yes", "No"].index(sponsor_default)
        except ValueError:
            sponsor_index = 1
        extra[category]["us_citizen_sponsor"] = st.selectbox(
            "Is there a US citizen sponsor?", ["Yes", "No"], index=sponsor_index
        )
        met_default = extra[category].get("met_in_person", "No")
        try:
            met_index = ["Yes", "No"].index(met_default)
        except ValueError:
            met_index = 1
        extra[category]["met_in_person"] = st.selectbox(
            "Have you met in person?", ["Yes", "No"], index=met_index
        )
        extra[category]["relationship_length_months"] = st.number_input(
            "Relationship length (months)", value=int(extra[category].get("relationship_length_months", 0)), min_value=0, step=1
        )
        extra[category]["evidence_list"] = st.text_area(
            "Evidence list (brief) - photos, tickets, messages", value=extra[category].get("evidence_list", "")
        )

    else:
        st.info("No additional visa-specific fields for this visa type.")


def merge_extra(user_profile: Dict[str, Any], category: str, additions: Dict[str, Any]):
    if "extra" not in user_profile:
        user_profile["extra"] = {}
    if category not in user_profile["extra"]:
        user_profile["extra"][category] = {}
    # shallow merge
    user_profile["extra"][category].update(additions)


# --- Streamlit UI ---
st.title("Visa Eligibility Quick Evaluator")
st.write("Provide basic profile information and visa type; we'll ask for any missing details if needed.")

# Initialize session state for tracking form state across reruns
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "final_result" not in st.session_state:
    st.session_state.final_result = None
if "user_profile_state" not in st.session_state:
    st.session_state.user_profile_state = None

# Keep visa_type selection outside the form so we can dynamically render fields inside the form
visa_type_options = ["F1 Student", "H1B Work", "B1/B2 Visitor", "K1 Fiance", "Other"]
selected_visa_type = st.selectbox("Select visa type", visa_type_options)
category = get_category(selected_visa_type)

with st.form(key="initial_form"):
    age = st.text_input("Age")
    nationality = st.text_input("Nationality")
    education = st.text_input("Education")
    employment = st.text_input("Employment")
    income = st.text_input("Income")

    # prepare user_profile and extra bucket
    user_profile: Dict[str, Any] = {
        "age": age,
        "nationality": nationality,
        "education": education,
        "employment": employment,
        "income": income,
        "visa_type": selected_visa_type,
        "extra": {}
    }

    st.markdown("---")
    st.subheader("Visa-specific fields")
    # Create a temporary dict to collect extra in form; will be merged into user_profile on submit
    temp_extra: Dict[str, Any] = {}
    render_visa_specific_inputs(category, temp_extra)

    submitted = st.form_submit_button("Evaluate")

if submitted:
    st.session_state.form_submitted = True
    # merge temp_extra into the user profile under category
    merge_extra(user_profile, category, temp_extra.get(category, {}))

    # Normalize some simple fields
    try:
        user_profile["age"] = int(user_profile.get("age")) if str(user_profile.get("age")).strip().isdigit() else user_profile.get("age")
    except Exception:
        pass

    # Store the user profile for reuse when submitting missing info
    st.session_state.user_profile_state = user_profile

    st.info("Running evaluation... (this may take a few seconds)")
    # build a simple query text; the real function may use the profile for retrieval
    query_text = f"{selected_visa_type} requirements for {user_profile.get('nationality','') }"

    result = run_rag_for_query(user_profile, query_text)
    st.session_state.final_result = result

# Display results if form has been submitted and result exists
if st.session_state.form_submitted and st.session_state.final_result is not None:
    result = st.session_state.final_result
    user_profile = st.session_state.user_profile_state
    
    # Show provisional result
    st.subheader("Provisional result")
    st.write("Decision:", result.get("decision"))
    st.write("Confidence:", result.get("confidence"))
    st.write("Explanation:", result.get("explanation"))

    # Debug: allow developer to inspect raw output and returned structure
    if st.checkbox("Show raw / debug output"):
        st.markdown("**Raw response object**")
        st.json(result)

    # Check for missing information returned by the evaluation
    missing: List[str] = result.get("missing_information") or []

    if missing:
        st.warning("We need more info to decide — please provide:")

        # We'll render an expander to collect only the missing fields
        with st.expander("Provide missing information", expanded=True):
            missing_inputs: Dict[str, Any] = {}

            for key in missing:
                # allow missing keys to be either 'category.key' or just 'key'
                if "." in key:
                    cat, k = key.split(".", 1)
                else:
                    cat = category
                    k = key

                label = k.replace("_", " ").capitalize()

                # Map to an input type depending on known keys
                if k in ["university_acceptance", "i20_issued", "degree_equiv", "job_offer", "return_ticket", "us_citizen_sponsor", "met_in_person"]:
                    missing_inputs.setdefault(cat, {})[k] = st.selectbox(label, ["Yes", "No", "Unknown"]) if k in ["university_acceptance", "i20_issued", "degree_equiv"] else st.selectbox(label, ["Yes", "No"])                
                elif k in ["school_name", "employer_name", "invitation_host", "evidence_list", "test_scores", "proof_of_funds_amount"]:
                    missing_inputs.setdefault(cat, {})[k] = st.text_input(label)
                elif k in ["years_experience", "trip_duration_days", "relationship_length_months"]:
                    missing_inputs.setdefault(cat, {})[k] = st.number_input(label, min_value=0, step=1)
                elif k == "travel_purpose":
                    missing_inputs.setdefault(cat, {})[k] = st.selectbox(label, ["business", "tourism", "medical"])                
                else:
                    # fallback to text input
                    missing_inputs.setdefault(cat, {})[k] = st.text_input(label)

            col1, col2 = st.columns([1, 1])
            submit_missing = col1.button("Submit missing info")
            cancel = col2.button("Cancel")

            if submit_missing:
                # merge missing_inputs into the stored user_profile.extra and re-run evaluation
                for c, fields in missing_inputs.items():
                    merge_extra(user_profile, c, fields)

                st.session_state.user_profile_state = user_profile
                st.info("Re-running evaluation with additional info...")
                query_text = f"{user_profile.get('visa_type', '')} requirements for {user_profile.get('nationality','') }"
                result2 = run_rag_for_query(user_profile, query_text)
                st.session_state.final_result = result2

                st.subheader("Final result")
                st.write("Decision:", result2.get("decision"))
                st.write("Confidence:", result2.get("confidence"))
                st.write("Explanation:", result2.get("explanation"))
                st.success("Evaluation complete!")

                # Debug output for final result
                if st.checkbox("Show final raw output"):
                    st.markdown("**Final raw response object**")
                    st.json(result2)

            elif cancel:
                st.error("User cancelled providing missing info. Showing provisional answer and missing keys.")
                st.subheader("Provisional answer")
                st.write("Decision:", result.get("decision"))
                st.write("Missing keys:", missing)

    else:
        st.success("Final decision (no additional information needed):")
        st.write("Decision:", result.get("decision"))
        st.write("Confidence:", result.get("confidence"))
        st.write("Explanation:", result.get("explanation"))

# End of file
