import os
import sys
import json
import time
from typing import List, Dict, Any

# Ensure src is on path so we can import local modules
BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, ROOT_DIR)

# Local workspace imports (uses your existing retrieval function)
# Importing `rag_inference.retrieve` can be heavy at import-time (loads embeddings/vectorstore).
# Use a lazy-safe import: provide a fallback stub so unit tests can import this module
# without bringing in heavy dependencies. The real `retrieve` will be imported when
# `run_rag_for_query` is executed in a full environment.
try:
    from rag_inference import retrieve  # -> [src/rag_inference.py]
except Exception:
    def retrieve(query, k=5, user_profile=None):
        # Minimal stub used in test contexts where the vectorstore or embeddings are unavailable
        return []

# Optional: load .env if python-dotenv installed
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT_DIR, ".env"))
except Exception:
    pass

# Try to import google/genai client but tolerate different shapes
GENAI_AVAILABLE = False
try:
    import genai
    GENAI_AVAILABLE = True
except Exception:
    try:
        # older import shape
        from google import generativeai as genai  # type: ignore
        GENAI_AVAILABLE = True
    except Exception:
        GENAI_AVAILABLE = False

LOG_PATH = os.path.join(BASE_DIR, "logs", "queries_gemini.jsonl")
TEMPLATE_PATH = os.path.join(BASE_DIR, "initial_prompt_template.txt")
TOP_K = int(os.getenv("TOP_K", "5"))

def build_retrieved_context(
    docs: List[Any], max_excerpt_chars: int = 800
) -> (str, List[Dict[str, Any]]):
    """
    Build the retrieved_context string for the prompt and a simple docs_used list for logging.
    """
    parts = []
    docs_used = []
    
    # If no docs returned from the retriever, try to provide a minimal
    # fallback by loading a few local policy files so the LLM has context.
    if not docs:
        try:
            fallback_dir = os.path.join(ROOT_DIR, "data", "cleaned_policies")
            if os.path.isdir(fallback_dir):
                files = [f for f in os.listdir(fallback_dir) if f.lower().endswith('.txt')]
                for i, fname in enumerate(files[:3], 1):
                    p = os.path.join(fallback_dir, fname)
                    try:
                        with open(p, 'r', encoding='utf-8') as fh:
                            content = fh.read().strip().replace('\n', ' ')[:max_excerpt_chars]
                        doc_id = fname
                        parts.append(f"[{i}] {doc_id}: {content}")
                        docs_used.append({
                            "id": doc_id,
                            "country": "UNKNOWN",
                            "visa_type": "UNKNOWN",
                            "excerpt": content[:100] + "..." if len(content) > 100 else content,
                            "fallback": True,
                        })
                    except Exception:
                        continue
                if parts:
                    return "\n".join(parts), docs_used
        except Exception:
            pass

        return "No relevant documents found.", []
        
    for i, d in enumerate(docs, 1):
        try:
            # Get metadata safely
            meta = {}
            if hasattr(d, "metadata"):
                meta = d.metadata if d.metadata is not None else {}
            
            # Extract document identifiers
            doc_id = meta.get("id", f"doc_{i}")
            country = meta.get("country", "UNKNOWN")
            visa_type = meta.get("visa_type", "UNKNOWN")
            
            # Get content safely
            content = ""
            if hasattr(d, "page_content"):
                content = d.page_content
            elif isinstance(d, (str, bytes)):
                content = str(d)
            else:
                content = str(d)
                
            # Clean and truncate content
            excerpt = content.strip().replace("\n", " ")[:max_excerpt_chars]
            if not excerpt:
                continue
                
            # Build context entry
            parts.append(f"[{i}] {doc_id} ({country}, {visa_type}): {excerpt}")
            docs_used.append({
                "id": doc_id,
                "country": country,
                "visa_type": visa_type,
                "excerpt": excerpt[:100] + "..." if len(excerpt) > 100 else excerpt
            })
        except Exception as e:
            print(f"Warning: Error processing document {i}: {e}", file=sys.stderr)
            continue
    
    if not parts:
        return "Failed to process documents.", []
        
    return "\n\n".join(parts), docs_used


def load_template() -> str:
    if os.path.exists(TEMPLATE_PATH):
        return open(TEMPLATE_PATH, "r", encoding="utf-8").read()
    # fallback simple template
    return (
        "You are a visa eligibility officer. Using the retrieved immigration policy context,\n"
        "evaluate whether the user meets the eligibility criteria for the given visa type.\n\n"
        "### Context:\n{retrieved_context}\n\n"
        "### User Information:\nAge: {age}\nNationality: {nationality}\nEducation: {education}\nEmployment: {employment}\nIncome: {income}\nVisa Type: {visa_type}\n\n"
        "### Instruction:\nProvide a clear eligibility decision (Likely Eligible / Likely Ineligible / Insufficient Data)\n"
        "and briefly explain your reasoning in plain English.\n"
    )


def make_full_prompt(user_profile: Dict[str, str], retrieved_context: str) -> str:
    template = load_template()
    filled = template.format(
        retrieved_context=retrieved_context,
        age=user_profile.get("age", "Unknown"),
        nationality=user_profile.get("nationality", "Unknown"),
        education=user_profile.get("education", "Unknown"),
        employment=user_profile.get("employment", "Unknown"),
        income=user_profile.get("income", "Unknown"),
        visa_type=user_profile.get("visa_type", "Unknown"),
    )
    
    # Enhanced instructions for better model guidance
    # Add explicit user_profile.extra details so the model can inspect which fields exist
    extra = user_profile.get("extra", {})
    try:
        extra_json = json.dumps(extra, ensure_ascii=False)
    except Exception:
        extra_json = str(extra)

    filled += (
        "\n\nBased on the provided immigration policy context and user information above, make a visa eligibility assessment using ONLY the facts from the retrieved documents."
        "\n\nBelow is the structured `extra` information supplied by the user (may be empty):\n"
        f"{extra_json}\n\n"
        "Your output MUST be valid JSON with these exact fields:\n"
        "- decision: string, one of [Likely Eligible, Likely Ineligible, Insufficient Data]\n"
        "- explanation: string, clear reasoning citing specific policy points and document indices\n"
        "- confidence: integer 0-100, your confidence in this assessment\n"
        "- citations: array of document indices (e.g. [1,2]) that support your decision\n"
        "- missing_information: array of strings describing any missing user inputs required to make a final decision (use dotted keys when helpful, e.g. f1.i20_issued)\n\n"
        "If some required facts are not present in the `extra` section, set decision to \"Insufficient Data\" and list the needed keys under missing_information. If you can decide, return an empty list for missing_information.\n\n"
        "Example output format:\n"
        '{"decision": "Likely Eligible", "explanation": "Based on document [1]...", "confidence": 85, "citations": [1,3], "missing_information": []}\n'
        "Your response (only JSON):"
    )
    return filled


def call_gemini(prompt: str, max_retries: int = 3, model_name: str = "models/gemini-2.0-flash") -> str:
    """Call Gemini with retries and rate limit handling."""
    # Prefer OpenAI if OPENAI_API_KEY is set (best-effort), otherwise try google genai
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    retry_delay = 5  # seconds between retries

    # Try OpenAI path if available
    if openai_key:
        try:
            import openai

            openai.api_key = openai_key
            for attempt in range(max_retries):
                try:
                    resp = openai.ChatCompletion.create(
                        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2,
                        max_tokens=1024,
                    )
                    # Extract text safely
                    choices = resp.get("choices") or []
                    if choices:
                        return choices[0].get("message", {}).get("content", "")
                    return str(resp)
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    raise
        except Exception:
            # fall through to google path if available
            pass

    # Try Google GenAI path
    if google_key and GENAI_AVAILABLE:
        try:
            import google.generativeai as genai

            genai.configure(api_key=google_key)
            # Configure generation parameters for more stable output
            generation_config = {
                "temperature": 0.2,  # Lower for more consistent output
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }

            for attempt in range(max_retries):
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(contents=prompt, generation_config=generation_config)
                    if hasattr(response, "text"):
                        return response.text
                    elif hasattr(response, "parts"):
                        return " ".join(part.text for part in response.parts)
                    else:
                        return str(response)
                except Exception as e:
                    error_msg = str(e).lower()
                    if "429" in error_msg or "resource exhausted" in error_msg:
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    raise
        except Exception:
            pass

    # If we reach here, no usable API was available or all calls failed
    raise RuntimeError("No available LLM API configured or all generation attempts failed")


def parse_json_from_text(text: str) -> Dict[str, Any]:
    """
    Attempt to find the first JSON object in the model output and parse it.
    """
    if not text:
        return {
            "decision": "Insufficient Data",
            "explanation": "No response from model",
            "confidence": 0,
            "citations": [],
        }
        
    # First try: direct JSON parse
    try:
        return json.loads(text)
    except Exception:
        pass
    
    # Second try: find JSON-like substring
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
            return json.loads(candidate)
    except Exception:
        pass
        
    # Third try: parse key-value pairs from text
    try:
        if "decision" in text.lower():
            lines = text.split("\n")
            decision = None
            explanation = []
            confidence = 0
            citations = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if "decision:" in line.lower():
                    decision = line.split(":", 1)[1].strip()
                elif "explanation:" in line.lower():
                    explanation.append(line.split(":", 1)[1].strip())
                elif "confidence:" in line.lower():
                    try:
                        confidence = int(line.split(":", 1)[1].strip().replace("%", ""))
                    except:
                        pass
                elif "citations:" in line.lower() or "sources:" in line.lower():
                    try:
                        citations = [int(x.strip()) for x in line.split(":", 1)[1].strip("[]").split(",")]
                    except:
                        pass
                elif line and not ":" in line and explanation:
                    explanation.append(line)
                    
            if decision:
                return {
                    "decision": decision,
                    "explanation": " ".join(explanation) if explanation else "No explanation provided",
                    "confidence": confidence,
                    "citations": citations
                }
    except Exception:
        pass
            
    # Fallback: return raw text with normalized structure
    return {
        "decision": "Insufficient Data",
        "explanation": text.strip() or "Failed to parse model output",
        "confidence": 30,
        "citations": [],
        "missing_information": [],
    }


def _normalize_parsed(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure the parsed object contains expected keys with sensible types.
    """
    out: Dict[str, Any] = {}
    out["decision"] = parsed.get("decision") or parsed.get("Decision") or "Insufficient Data"
    out["explanation"] = parsed.get("explanation") or parsed.get("Explanation") or ""

    # Confidence: allow string or number, normalize to int 0-100
    conf = parsed.get("confidence") or parsed.get("Confidence") or 0
    try:
        conf_val = int(float(str(conf).strip().replace("%", "")))
    except Exception:
        conf_val = 0
    conf_val = max(0, min(100, conf_val))
    out["confidence"] = conf_val

    # citations: try parse into list[int]
    citations = parsed.get("citations") or parsed.get("citation") or []
    if isinstance(citations, str):
        try:
            citations = json.loads(citations)
        except Exception:
            # try to extract numbers
            import re

            citations = [int(x) for x in re.findall(r"\d+", citations)]
    citations_list = []
    try:
        for v in citations:
            citations_list.append(int(v))
    except Exception:
        citations_list = []
    out["citations"] = citations_list

    # missing_information: normalize to list[str]
    missing = parsed.get("missing_information") or parsed.get("missing") or []
    if isinstance(missing, str):
        try:
            missing = json.loads(missing)
        except Exception:
            missing = [m.strip() for m in missing.split(",") if m.strip()]
    if not isinstance(missing, list):
        missing = []
    out["missing_information"] = [str(x) for x in missing]

    return out


def heuristic_assessment(user_profile: Dict[str, Any], docs_used: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic heuristic used when an LLM API key is not configured. This returns
    a structured response and lists missing fields (dotted keys) when needed.
    """
    visa_type = (user_profile.get("visa_type") or "").lower()
    extra = user_profile.get("extra", {})
    missing = []
    decision = "Insufficient Data"
    confidence = 30
    explanation_parts = []

    def check_and_add(cat, key):
        val = extra.get(cat, {}).get(key)
        if val is None or (isinstance(val, str) and val.strip() == "") or val == "Unknown":
            missing.append(f"{cat}.{key}")
            return False
        return True

    if "f1" in visa_type or "student" in visa_type:
        # F1 requires university acceptance, I-20, and proof of funds
        ok_accept = check_and_add("f1", "university_acceptance")
        ok_i20 = check_and_add("f1", "i20_issued")
        ok_funds = check_and_add("f1", "proof_of_funds_amount")

        if missing:
            decision = "Insufficient Data"
            explanation_parts.append("Missing required student visa inputs: " + ", ".join(missing))
            confidence = 25
        else:
            # simple heuristic: if all present and i20_issued == Yes -> likely eligible
            i20 = extra.get("f1", {}).get("i20_issued", "").lower()
            if i20.startswith("y"):
                decision = "Likely Eligible"
                confidence = 80
                explanation_parts.append("User has university acceptance, I-20 issued and proof of funds present.")
            else:
                decision = "Likely Ineligible"
                confidence = 30
                explanation_parts.append("I-20 not issued or explicitly negative.")

    elif "h1" in visa_type or "work" in visa_type:
        # H1B requires: job offer, employer, and degree (BA/equivalent)
        job_offer = extra.get("h1", {}).get("job_offer", "").lower()
        degree_equiv = extra.get("h1", {}).get("degree_equiv", "").lower()
        years_exp = extra.get("h1", {}).get("years_experience", 0)
        
        # Try to parse years_experience as int
        try:
            years_exp = int(years_exp) if years_exp else 0
        except Exception:
            years_exp = 0
        
        if job_offer.startswith("n"):
            # Explicitly "No" job offer -> ineligible
            decision = "Likely Ineligible"
            confidence = 25
            explanation_parts.append("No job offer provided.")
        else:
            # Check for missing required fields (only if job_offer not explicitly "No")
            ok_job = check_and_add("h1", "job_offer")
            ok_employer = check_and_add("h1", "employer_name")
            
            if missing:
                decision = "Insufficient Data"
                explanation_parts.append("Missing H1B information: " + ", ".join(missing))
                confidence = 20
            else:
                # If degree equivalency is explicitly 'No', mark ineligible
                if degree_equiv.startswith("n"):
                    decision = "Likely Ineligible"
                    confidence = 20
                    explanation_parts.append("Degree equivalency not established; likely ineligible for H1B.")
                elif job_offer.startswith("y"):
                    # Job offer is present AND degree equivalency is established (Yes) or degree_equiv is blank/Unknown
                    # With job offer, if user claims degree equivalency explicitly 'Yes', OR has substantial experience (5+ years)
                    if degree_equiv.startswith("y") or years_exp >= 5:
                        decision = "Likely Eligible"
                        confidence = 75
                        if years_exp >= 5 and degree_equiv.startswith("y"):
                            explanation_parts.append("Job offer present with strong experience and degree equivalency established.")
                        elif degree_equiv.startswith("y"):
                            explanation_parts.append("Job offer present with degree equivalency established.")
                        else:
                            explanation_parts.append("Job offer present with substantial work experience (5+ years).")
                    else:
                        # Job offer but degree equivalency unclear and less experience
                        decision = "Insufficient Data"
                        confidence = 50
                        explanation_parts.append("Job offer present but degree equivalency needs clarification.")
                else:
                    decision = "Likely Ineligible"
                    confidence = 25
                    explanation_parts.append("No job offer provided.")

    elif "b1" in visa_type or "b2" in visa_type or "visitor" in visa_type:
        ok_return = check_and_add("b1b2", "return_ticket")
        if missing:
            decision = "Insufficient Data"
            explanation_parts.append("Missing visitor info: " + ", ".join(missing))
            confidence = 30
        else:
            rt = extra.get("b1b2", {}).get("return_ticket", "").lower()
            purpose = extra.get("b1b2", {}).get("travel_purpose", "").lower()
            invitation = extra.get("b1b2", {}).get("invitation_host", "")
            if rt.startswith("y"):
                # Increase confidence for business trips with invitation host
                if "business" in purpose and invitation:
                    decision = "Likely Eligible"
                    confidence = 75
                    explanation_parts.append("Return ticket present and business invitation exist; likely eligible.")
                else:
                    decision = "Likely Eligible"
                    # Slightly increase confidence for well-documented trips
                    confidence = 70 if "business" in purpose else 65
                    explanation_parts.append("Return ticket present; purpose and duration appear reasonable.")
            else:
                decision = "Likely Ineligible"
                confidence = 30
                explanation_parts.append("No return ticket booked.")

    elif "k1" in visa_type or "fiance" in visa_type:
        # Check if met_in_person is explicitly "No" -> ineligible immediately
        met_in_person = extra.get("k1", {}).get("met_in_person", "").lower()
        
        if met_in_person.startswith("n"):
            # Explicitly "No" meeting -> ineligible
            decision = "Likely Ineligible"
            confidence = 25
            explanation_parts.append("Fiancee and sponsor must have met in person.")
        else:
            # Check for missing required fields (only if met_in_person not explicitly "No")
            ok_sponsor = check_and_add("k1", "us_citizen_sponsor")
            ok_met = check_and_add("k1", "met_in_person")
            
            if missing:
                decision = "Insufficient Data"
                explanation_parts.append("Missing K1 info: " + ", ".join(missing))
                confidence = 20
            else:
                    sponsor_yes = extra.get("k1", {}).get("us_citizen_sponsor", "").lower().startswith("y")
                    if sponsor_yes:
                        # Boost confidence for stronger evidence
                        rel_len = 0
                        try:
                            rel_len = int(extra.get("k1", {}).get("relationship_length_months", 0))
                        except Exception:
                            rel_len = 0

                        evidence = str(extra.get("k1", {}).get("evidence_list", "")).lower()
                        # Default eligible
                        decision = "Likely Eligible"
                        confidence = 70
                        explanation_parts.append("US citizen sponsor and meeting information present.")

                        # Long relationships are stronger
                        if rel_len >= 24:
                            confidence = 85
                            explanation_parts.append("Long relationship duration strengthens eligibility.")
                        # Financial affidavit (I-864) increases confidence
                        if "i-864" in evidence or "i864" in evidence or "i 864" in evidence:
                            confidence = max(confidence, 80)
                            explanation_parts.append("Sponsor financial affidavit (I-864) present; increases confidence.")
                    else:
                        decision = "Likely Ineligible"
                        confidence = 25
                        explanation_parts.append("No US citizen sponsor indicated.")

    else:
        # Generic fallback: if no visa-specific rules, check there is at least a nationality and some context
        if not user_profile.get("nationality"):
            missing.append("nationality")
            decision = "Insufficient Data"
            confidence = 20
            explanation_parts.append("Nationality missing.")
        else:
            decision = "Insufficient Data"
            confidence = 30
            explanation_parts.append("No specific visa rules applied; provide more details.")

    return {
        "decision": decision,
        "explanation": " ".join(explanation_parts) or "No rationale generated.",
        "confidence": confidence,
        "citations": [],
        "missing_information": missing,
    }


def log_query(entry: Dict[str, Any]):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_rag_for_query(
    user_profile: Dict[str, str], query_text: str, top_k: int = TOP_K
) -> Dict[str, Any]:
    # 1) retrieve with enhanced profile context
    docs = retrieve(query_text, k=top_k, user_profile=user_profile)
    retrieved_context, docs_used = build_retrieved_context(docs)

    # 2) construct prompt
    prompt = make_full_prompt(user_profile, retrieved_context)

    # 3) call LLM (Gemini/OpenAI) defensively; if no API keys, use heuristic fallback
    raw_output = None
    parsed = None
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    if not openai_key and not google_key:
        # No API keys configured: use heuristic to produce deterministic result (useful for testing)
        parsed = heuristic_assessment(user_profile, docs_used)
        raw_output = "[HEURISTIC_FALLBACK]"
    else:
        try:
            raw_output = call_gemini(prompt, max_retries=3, model_name="models/gemini-2.0-flash")
        except Exception as e:
            # If LLM fails, fall back to heuristic rather than crashing
            try:
                parsed = heuristic_assessment(user_profile, docs_used)
                raw_output = f"[FALLBACK_HEURISTIC] {e}"
            except Exception:
                raw_output = f"[ERROR] Failed to call LLM and heuristic fallback: {e}"

        if parsed is None:
            # parse model output (expecting JSON)
            try:
                parsed_raw = parse_json_from_text(raw_output)
            except Exception:
                parsed_raw = {"decision": "Insufficient Data", "explanation": raw_output, "confidence": 0, "citations": [], "missing_information": []}
            parsed = _normalize_parsed(parsed_raw)
            
            # If LLM returned "Insufficient Data" with no docs AND we have a complete profile, use heuristic instead
            # This handles cases where the vectorstore returned no relevant docs
            if parsed.get("decision") == "Insufficient Data" and not docs_used and len(docs) == 0:
                # Check if profile is actually complete (has visa-specific extra fields)
                extra = user_profile.get("extra", {})
                visa_type = user_profile.get("visa_type", "").lower()
                
                # If we have visa-specific fields populated, trust the heuristic over empty-context LLM
                has_visa_fields = False
                if "f1" in visa_type and extra.get("f1"):
                    has_visa_fields = True
                elif "h1" in visa_type and extra.get("h1"):
                    has_visa_fields = True
                elif ("b1" in visa_type or "b2" in visa_type) and extra.get("b1b2"):
                    has_visa_fields = True
                elif "k1" in visa_type and extra.get("k1"):
                    has_visa_fields = True
                
                if has_visa_fields:
                    # Use heuristic as it's more reliable than LLM without context
                    parsed = heuristic_assessment(user_profile, docs_used)
                    raw_output = f"[HEURISTIC_OVERRIDE] LLM returned insufficient data with no docs; using heuristic instead"

            # If LLM returned "Insufficient Data" but the docs we have are only fallback local policies,
            # the LLM may still be conservative. In that case, prefer the heuristic when user provided visa fields.
            if parsed.get("decision") == "Insufficient Data" and docs_used:
                try:
                    any_fallback = any(d.get("fallback") for d in docs_used if isinstance(d, dict))
                except Exception:
                    any_fallback = False

                if any_fallback:
                    extra = user_profile.get("extra", {})
                    visa_type = user_profile.get("visa_type", "").lower()
                    has_visa_fields = False
                    if "f1" in visa_type and extra.get("f1"):
                        has_visa_fields = True
                    elif "h1" in visa_type and extra.get("h1"):
                        has_visa_fields = True
                    elif ("b1" in visa_type or "b2" in visa_type) and extra.get("b1b2"):
                        has_visa_fields = True
                    elif "k1" in visa_type and extra.get("k1"):
                        has_visa_fields = True

                    if has_visa_fields:
                        parsed = heuristic_assessment(user_profile, docs_used)
                        raw_output = f"[HEURISTIC_OVERRIDE] LLM returned insufficient data with only fallback docs; using heuristic instead"

    # 5) build final response object
    # Ensure parsed is normalized
    if parsed is None:
        parsed = {"decision": "Insufficient Data", "explanation": "No output", "confidence": 0, "citations": [], "missing_information": []}
    else:
        # If parsed came from heuristic, ensure it is normalized
        try:
            parsed = _normalize_parsed(parsed)
        except Exception:
            # already normalized probably
            pass

    response = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "user_profile": user_profile,
        "query_text": query_text,
        "docs_used": docs_used,
        "prompt_len": len(prompt),
        "raw_output": raw_output,
        "decision": parsed.get("decision"),
        "explanation": parsed.get("explanation"),
        "confidence": parsed.get("confidence"),
        "citations": parsed.get("citations", []),
        "missing_information": parsed.get("missing_information", []),
    }

    # 6) log to file
    try:
        log_query(response)
    except Exception:
        pass

    return response


if __name__ == "__main__":
    # Example usage with B1/B2 visa type
    user = {
        "age": "35",
        "nationality": "India",
        "education": "Bachelor's",
        "employment": "Business Owner",
        "income": "50000",
        "visa_type": "B1/B2 Visitor",
    }

    # Enhanced query based on visa type and profile data
    visa_type = user.get("visa_type", "").lower()
    nationality = user.get("nationality", "")
    education = user.get("education", "")
    employment = user.get("employment", "")
    income = user.get("income", "")

    # Build specific query based on visa type
    base_query = ""
    if "b1" in visa_type or "b2" in visa_type or "business" in visa_type or "tourist" in visa_type:
        base_query = "B1/B2 visitor visa requirements eligibility criteria"
    elif "h1b" in visa_type or "work" in visa_type:
        base_query = "H1B work visa requirements eligibility criteria"
    elif "k1" in visa_type or "fiance" in visa_type:
        base_query = "K1 fiance visa requirements eligibility criteria"
    else:  # Default to F1 student
        base_query = "F1 student visa requirements eligibility criteria"
    
    # Add profile-specific terms to help target relevant documents
    profile_terms = []
    if nationality:
        profile_terms.append(f"{nationality} nationality citizenship country of origin residence")
    if education:
        profile_terms.append(f"{education} academic background education degree qualification previous study")
    if employment:
        profile_terms.append(f"{employment} employment work status")
    if income:
        profile_terms.append(f"{income} financial resources bank statements support funds")
    if visa_type:
        profile_terms.append(f"{visa_type} visa category type class classification")
    
    # Combine the base query with profile terms
    q = f"{base_query} for {nationality} purpose of travel documentation financial requirements"
    print("\nDebug: Using enhanced query:", q)
    
    # Add profile terms for deeper search
    q2 = f"{q} {' '.join(profile_terms)}"
    print("\nDebug: Using enhanced query:", q2)
    
    # Run the full pipeline
    out = run_rag_for_query(user, q2, top_k=3)
    
    # Output results clearly
    print("\n=== Generated Prompt ===")
    docs = retrieve(q2, k=3)
    retrieved_context, _ = build_retrieved_context(docs)
    prompt = make_full_prompt(user, retrieved_context)
    print(prompt)
    
    print("\n=== Raw Model Output ===")
    print(out["raw_output"])
    
    print("\n=== Final Results ===")
    print("Decision:", out["decision"])
    print("Confidence:", out["confidence"])
    print("Explanation:", out["explanation"])
    print("Citations:", out["citations"])