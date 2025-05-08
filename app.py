# app.py
from flask import Flask, request, render_template, jsonify
import calculator
import nlp_service # Our new NLP module

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index_page():
    return render_template("index.html", query="", result_text="")

@app.route("/calculate", methods=["POST"])
def calculate_financials():
    user_query = request.form.get("query")
    if not user_query:
        return render_template("index.html", query="", result_text="Error: No query provided.")

    # 1. Get Intent
    intent_key, intent_confidence = nlp_service.get_intent(user_query)
    
    result_text = ""
    calculation_details = ""

    if not intent_key:
        result_text = "Error: Could not understand your request. Please try rephrasing."
        return render_template("index.html", query=user_query, result_text=result_text)

    # Optional: Check intent confidence
    # if intent_confidence < 0.7: # Adjust threshold as needed
    #     result_text = f"Warning: Low confidence ({intent_confidence:.2f}) in understanding intent. Interpreted as: {intent_key.replace('_', ' ').title()}"
    # else:
    #     result_text = f"Intent: {intent_key.replace('_', ' ').title()}\n"
    
    calculation_details += f"Interpreted Action: {nlp_service.CANDIDATE_INTENTS_LABELS[list(nlp_service.INTENT_LABEL_TO_KEY_MAP.values()).index(intent_key)]}\n"


    # 2. Extract Entities (Parameters) based on intent
    entities, error_message = nlp_service.extract_entities(user_query, intent_key)

    if error_message:
        result_text += f"Error extracting parameters: {error_message}"
        return render_template("index.html", query=user_query, result_text=result_text, calculation_details=calculation_details)

    if not entities:
        result_text += "Error: Could not extract necessary values from your query."
        return render_template("index.html", query=user_query, result_text=result_text, calculation_details=calculation_details)

    calculation_details += f"Extracted Values: {entities}\n"

    # 3. Call Calculator Function
    try:
        intent_config = nlp_service.INTENT_CONFIG[intent_key]
        calc_func_name = intent_config["calculator_function_name"]
        
        # Prepare arguments for the calculator function
        # Rates are expected as percentages from NLP, convert to decimal for calculator
        args_for_calc = {}
        valid_call = True
        
        for param_name, value in entities.items():
            if param_name.endswith("_percent"): # e.g., rate_percent, annual_rate_percent
                args_for_calc[param_name.replace("_percent", "")] = value / 100.0
            elif param_name == "time_years": # for simple interest
                 args_for_calc["time"] = value
            elif param_name == "term_months": # for loan amortization
                 args_for_calc["n_months"] = value
            elif param_name == "compounding_frequency":
                 args_for_calc["times_compounded_per_year"] = value
            else: # Handles future_value, present_value, principal, periods, years
                args_for_calc[param_name] = value
        
        # Ensure all required parameters for the specific function are present after mapping
        # This is a simplified check; more robust mapping might be needed if param names differ greatly
        # between NLP extraction and calculator function signatures. For now, we assume close mapping.

        # Example: Get the actual calculator function
        if hasattr(calculator, calc_func_name):
            calculator_function = getattr(calculator, calc_func_name)
            
            # Dynamically call the function with extracted and mapped arguments
            # This requires careful alignment of NLP param names and function arg names
            # For simplicity, we'll use if/else based on intent_key for now,
            # as direct mapping can be tricky with varying param names.

            numeric_result = None
            if intent_key == "calculate_present_value":
                numeric_result = calculator_function(fv=args_for_calc['future_value'], rate=args_for_calc['rate'], n_periods=args_for_calc['periods'])
                result_text = f"The Present Value is: ${numeric_result:,.2f}"
            elif intent_key == "calculate_future_value":
                numeric_result = calculator_function(pv=args_for_calc['present_value'], rate=args_for_calc['rate'], n_periods=args_for_calc['periods'])
                result_text = f"The Future Value is: ${numeric_result:,.2f}"
            elif intent_key == "calculate_simple_interest":
                numeric_result = calculator_function(principal=args_for_calc['principal'], rate=args_for_calc['rate'], time=args_for_calc['time'])
                result_text = f"The Simple Interest earned is: ${numeric_result:,.2f}"
            elif intent_key == "calculate_compound_interest":
                numeric_result = calculator_function(principal=args_for_calc['principal'], 
                                                     annual_rate=args_for_calc['annual_rate'], 
                                                     times_compounded_per_year=args_for_calc['times_compounded_per_year'], 
                                                     years=args_for_calc['years'])
                result_text = f"The total amount with Compound Interest (Future Value) is: ${numeric_result:,.2f}"
            elif intent_key == "calculate_monthly_loan_payment":
                numeric_result = calculator_function(principal=args_for_calc['principal'], 
                                                     annual_rate=args_for_calc['annual_rate'], 
                                                     n_months=args_for_calc['n_months'])
                result_text = f"The Monthly Loan Payment is: ${numeric_result:,.2f}"
            else:
                result_text = "Error: Calculation logic for this intent is not implemented yet."
                valid_call = False

            if valid_call and numeric_result is not None:
                 calculation_details += f"Calculation: {calc_func_name}({', '.join(f'{k}={v:.4f}' if isinstance(v, float) else f'{k}={v}' for k, v in args_for_calc.items() if k in calculator_function.__code__.co_varnames)})\n"
                 calculation_details += f"Result: {numeric_result:.2f}"


        else:
            result_text = f"Error: Calculator function '{calc_func_name}' not found."

    except ValueError as ve: # Catch specific errors from calculator functions
        result_text = f"Calculation Error: {ve}"
    except TypeError as te: # Catch argument mismatch errors
        result_text = f"Parameter Mismatch Error: Could not perform calculation. {te}. Check extracted values: {args_for_calc}"
    except Exception as e:
        result_text = f"An unexpected error occurred during calculation: {e}"

    return render_template("index.html", query=user_query, result_text=result_text, calculation_details=calculation_details)


if __name__ == "__main__":
    # Create the 'templates' directory if it doesn't exist
    import os
    if not os.path.exists("templates"):
        os.makedirs("templates")
    # Check if index.html exists, if not, create a basic one
    if not os.path.exists("templates/index.html"):
        with open("templates/index.html", "w") as f_html:
            f_html.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial NLP Calculator</title>
    <style>
        body { font-family: sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
        .container { max-width: 600px; margin: auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"] { width: calc(100% - 22px); padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 4px; }
        button { background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #0056b3; }
        .result, .details { margin-top: 20px; padding: 15px; border: 1px solid #eee; border-radius: 4px; background-color: #e9f7ef; }
        .result h3, .details h3 { margin-top: 0; color: #196f3d; }
        .details { background-color: #f0f0f0; font-family: monospace; white-space: pre-wrap; font-size: 0.9em; }
        .error { background-color: #f8d7da; color: #721c24; border-color: #f5c6cb;}
    </style>
</head>
<body>
    <div class="container">
        <h1>Financial NLP Calculator</h1>
        <form action="/calculate" method="post">
            <label for="query">Ask a financial question:</label>
            <input type="text" id="query" name="query" value="{{ query }}" placeholder="e.g., What is the future value of $1000 at 5% for 10 years?">
            <button type="submit">Calculate</button>
        </form>

        {% if result_text %}
            <div class="result {% if 'Error:' in result_text or 'Warning:' in result_text %}error{% endif %}">
                <h3>Result:</h3>
                <p>{{ result_text }}</p>
            </div>
        {% endif %}

        {% if calculation_details %}
            <div class="details">
                <h3>Calculation Process:</h3>
                <p>{{ calculation_details }}</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
            """)
    app.run(debug=True)