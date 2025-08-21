# Financial NLP Calculator

A Flask web application that uses Hugging Face Transformers to understand natural language queries for financial calculations.

## Features

* Interprets natural language to identify the desired financial calculation (e.g., Present Value, Loan Payment).
* Extracts numerical values (principal, rate, time, etc.) from the user's query.
* Supports calculations for:
    * Present Value
    * Future Value
    * Simple Interest
    * Compound Interest
    * Monthly Loan Payments

## Project Structure

financial_nlp_calculator/
├── app.py              # Main Flask application
├── calculator.py       # Financial calculation functions
├── nlp_service.py      # NLP logic (intent recognition, entity extraction)
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html    # HTML frontend for user interaction
├── .gitignore          # Specifies intentionally untracked files
└── README.md           # This documentation file

## Setup Instructions

1.  **Clone the Repository (or Prepare Your Project Folder):**
    If you've already created the project locally, you'll initialize Git in this folder. If you create the GitHub repo first, you'll clone it.

2.  **Create and Activate a Virtual Environment (Recommended):**
    Open your terminal or command prompt in the project's root directory:
    ```bash
    python -m venv venv
    ```
    Activate the environment:
    * On Windows: `venv\Scripts\activate`
    * On macOS/Linux: `source venv/bin/activate`

3.  **Install Dependencies:**
    With your virtual environment activated, install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: The first time you run the application, Hugging Face Transformers will download the pre-trained NLP models. This may take some time and requires an internet connection. These models are cached locally on your system (usually outside the project directory).*

## How to Run the Application

1.  **Ensure your virtual environment is activated.**
2.  **Navigate to the project directory in your terminal.**
3.  **Run the Flask application:**
    ```bash
    python app.py
    ```
4.  Open your web browser and go to `http://127.0.0.1:5000/`.

## Technologies Used

* Python
* Flask (for the web application)
* Hugging Face Transformers (for NLP):
    * Zero-shot classification model (e.g., `valhalla/distilbart-mnli-12-3`) for intent recognition.
    * Question-answering model (e.g., `distilbert-base-cased-distilled-squad`) for entity extraction.
* HTML (for the frontend)

## Further Development / To-Do
* (Optional: Mention any features you plan to add or known issues you are working on, like improving NPV multi-cashflow extraction)
