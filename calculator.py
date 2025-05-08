# calculator.py
import math

def present_value(fv, rate, n_periods):
    """
    Calculates the present value.
    :param fv: Future Value
    :param rate: Interest rate per period (as a decimal, e.g., 0.05 for 5%)
    :param n_periods: Number of periods
    :return: Present Value
    """
    return fv / ((1 + rate) ** n_periods)

def future_value(pv, rate, n_periods):
    """
    Calculates the future value.
    :param pv: Present Value
    :param rate: Interest rate per period (as a decimal, e.g., 0.05 for 5%)
    :param n_periods: Number of periods
    :return: Future Value
    """
    return pv * ((1 + rate) ** n_periods)

def simple_interest(principal, rate, time):
    """
    Calculates the simple interest earned.
    :param principal: Principal amount
    :param rate: Annual interest rate (as a decimal, e.g., 0.05 for 5%)
    :param time: Time in years
    :return: Simple Interest Amount
    """
    return principal * rate * time

def compound_interest(principal, annual_rate, times_compounded_per_year, years):
    """
    Calculates the future value with compound interest.
    :param principal: Principal amount
    :param annual_rate: Annual interest rate (as a decimal, e.g., 0.05 for 5%)
    :param times_compounded_per_year: Number of times interest is compounded per year
    :param years: Number of years
    :return: Total amount after compound interest (Future Value)
    """
    if times_compounded_per_year <= 0:
        raise ValueError("Number of times compounded per year must be greater than 0.")
    rate_per_period = annual_rate / times_compounded_per_year
    n_periods = times_compounded_per_year * years
    return principal * ((1 + rate_per_period) ** n_periods)

def loan_amortization_payment(principal, annual_rate, n_months):
    """
    Calculates the monthly loan payment.
    :param principal: Loan principal amount
    :param annual_rate: Annual interest rate (as a decimal, e.g., 0.05 for 5%)
    :param n_months: Total number of months for the loan
    :return: Monthly payment amount
    """
    if n_months <= 0:
        raise ValueError("Number of months must be greater than 0.")
    if annual_rate < 0:
        raise ValueError("Annual rate cannot be negative.")
    
    if annual_rate == 0: # Handle zero interest rate separately
        return principal / n_months
        
    monthly_rate = annual_rate / 12
    payment = principal * (monthly_rate * ((1 + monthly_rate) ** n_months)) / (((1 + monthly_rate) ** n_months) - 1)
    return payment

# You can add more functions here like NPV, IRR, Annuities etc.
# For NPV and IRR, you'd need to handle lists of cashflows.

# Example: (Not used by the initial app.py but good to have)
import numpy as np # Add numpy to requirements.txt if you use this
def net_present_value(rate, cashflows):
    """
    Calculates Net Present Value.
    :param rate: Discount rate per period (decimal)
    :param cashflows: A list of cashflows (the first can be negative for initial investment)
    :return: NPV
    """
    return sum(cf / (1 + rate) ** i for i, cf in enumerate(cashflows))

def internal_rate_of_return(cashflows):
    """
    Calculates Internal Rate of Return. Requires numpy.
    :param cashflows: A list of cashflows
    :return: IRR
    """
    # Ensure numpy is installed and imported if this function is used.
    # return np.irr(cashflows)
    pass # Placeholder if numpy not yet a requirement