# nlp_service.py
from transformers import pipeline
import re

# --- Initialize Hugging Face Pipelines ---
# Using a smaller, efficient model for zero-shot classification.
# You can experiment with others like 'facebook/bart-large-mnli' for potentially higher accuracy.
intent_classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-3")

# Using a common model for question answering.
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# --- Configuration for Intents and Parameter Extraction ---

# Define the financial intents your calculator will understand
CANDIDATE_INTENTS_LABELS = [
    "Calculate Present Value",
    "Calculate Future Value",
    "Calculate Simple Interest",
    "Calculate Compound Interest",
    "Calculate Monthly Loan Payment"
]

# Map user-friendly labels to internal keys and define parameters + questions for QA
INTENT_CONFIG = {
    "calculate_present_value": {
        "parameters": {
            "future_value": "What is the future value or final amount?",
            "rate_percent": "What is the interest rate in percent?", # Expects e.g., 5 for 5%
            "periods": "How many periods (e.g., years)?"
        },
        "calculator_function_name": "present_value",
        "required_params": ["future_value", "rate_percent", "periods"]
    },
    "calculate_future_value": {
        "parameters": {
            "present_value": "What is the present value or initial investment amount?",
            "rate_percent": "What is the interest rate in percent?",
            "periods": "How many periods (e.g., years)?"
        },
        "calculator_function_name": "future_value",
        "required_params": ["present_value", "rate_percent", "periods"]
    },
    "calculate_simple_interest": {
    "parameters": {
        "principal": "What is the starting sum of money or principal?",
        "rate_percent": "What specific percentage is the interest rate?", 
        "time_years": "For how many years is the interest calculated?"  
    },
    "calculator_function_name": "simple_interest",
    "required_params": ["principal", "rate_percent", "time_years"]
},
    "calculate_compound_interest": {
        "parameters": {
            "principal": "What is the principal amount?",
            "annual_rate_percent": "What is the annual interest rate in percent?",
            "compounding_frequency": "How many times is the interest compounded per year?",
            "years": "For how many years is the investment?"
        },
        "calculator_function_name": "compound_interest",
        "required_params": ["principal", "annual_rate_percent", "compounding_frequency", "years"]
    },
   # In INTENT_CONFIG:
"calculate_monthly_loan_payment": {
    "parameters": {
        "principal": "What is the loan principal amount or total borrowed?", # Keep this or your previous good one
        "annual_rate_percent": "What is the annual interest rate in percent?", # Keep this
        "term_months": "For how many months does the loan last?" # <-- TRY THIS NEW QUESTION (or another from suggestions)
    },
    "calculator_function_name": "loan_amortization_payment",
    "required_params": ["principal", "annual_rate_percent", "term_months"]
}
}

# Mapping from readable labels to keys in INTENT_CONFIG
INTENT_LABEL_TO_KEY_MAP = {
    "Calculate Present Value": "calculate_present_value",
    "Calculate Future Value": "calculate_future_value",
    "Calculate Simple Interest": "calculate_simple_interest",
    "Calculate Compound Interest": "calculate_compound_interest",
    "Calculate Monthly Loan Payment": "calculate_monthly_loan_payment",
}

def get_intent(query):
    """
    Identifies the financial intent from the user's query.
    """
    try:
        result = intent_classifier(query, CANDIDATE_INTENTS_LABELS, multi_label=False)
        # Get the intent with the highest score
        top_intent_label = result['labels'][0]
        confidence = result['scores'][0]
        
        # Map the readable label to our internal key
        intent_key = INTENT_LABEL_TO_KEY_MAP.get(top_intent_label)
        
        if not intent_key:
            return None, 0.0 # Or raise an error
            
        return intent_key, confidence
    except Exception as e:
        print(f"Error in intent classification: {e}")
        return None, 0.0

def parse_numerical_value(answer_text):
    """
    Extracts a numerical value from a QA model's answer string.
    Handles simple numbers, decimals, and removes common symbols.
    """
    if not answer_text:
        return None
    
    # Remove common currency symbols, commas, and percentage signs for cleaner parsing
    # This helps if the model includes them in the answer span.
    cleaned_text = str(answer_text).replace('$', '').replace(',', '').replace('%', '').strip()
    
    # Regex to find numbers (integers or decimals)
    # This looks for sequences of digits, possibly with one decimal point.
    # It tries to capture numbers like "1000", "2.5", ".5"
    match = re.search(r'\b\d+\.?\d*\b|\b\.\d+\b', cleaned_text)
    
    if match:
        try:
            value = float(match.group(0))
            return value
        except ValueError:
            # If conversion fails, it wasn't a valid number string
            pass
            
    # Fallback or more sophisticated parsing (e.g., "five" to 5) could be added here.
    # For now, if the regex fails, we assume no clear number was found.
    print(f"Could not parse numerical value from: '{answer_text}' (cleaned: '{cleaned_text}')")
    return None


def extract_entities(query, intent_key):
    """
    Extracts numerical parameters for a given intent using Question Answering.
    """
    if not intent_key or intent_key not in INTENT_CONFIG:
        return None, "Invalid intent key."

    config = INTENT_CONFIG[intent_key]
    parameter_questions = config["parameters"]
    extracted_values = {}
    missing_params = []

    for param_name, question_text in parameter_questions.items():
        try:
            qa_result = qa_pipeline(question=question_text, context=query)
            # print(f"DEBUG: Intent: {intent_key}, Param: {param_name}, Question: '{question_text}' -> QA Raw Answer: '{qa_result['answer']}' (Score: {qa_result['score']:.4f})")
            if qa_result and qa_result['score'] > 0.1: # Confidence threshold for QA
                value = parse_numerical_value(qa_result['answer'])
                if value is not None:
                    extracted_values[param_name] = value
                else:
                    # QA found an answer, but we couldn't parse a number
                    print(f"Could not parse number for '{param_name}' from QA answer: '{qa_result['answer']}'")
                    if param_name in config.get("required_params", []):
                        missing_params.append(param_name)
            elif param_name in config.get("required_params", []):
                 missing_params.append(param_name)

        except Exception as e:
            print(f"Error extracting entity '{param_name}' with question '{question_text}': {e}")
            if param_name in config.get("required_params", []):
                missing_params.append(param_name)
    
    if missing_params:
        return extracted_values, f"Missing or unparsable required parameters: {', '.join(missing_params)}."
        
    return extracted_values, None # No error message means success