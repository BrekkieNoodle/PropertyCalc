import streamlit as st
import numpy as np
import pandas as pd
from io import BytesIO

# Mortgage calculation function
def calculate_mortgage_payment(principal, annual_rate, years, payments_per_year):
    r = annual_rate / payments_per_year
    n = years * payments_per_year
    payment = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    return payment

# Amortization schedule function
def generate_amortization_schedule(principal, annual_rate, years, payments_per_year, payment_amount):
    balance = principal
    payment_list, interest_list, principal_list = [], [], []

    for _ in range(int(years * payments_per_year)):
        interest_payment = balance * (annual_rate / payments_per_year)
        principal_payment = payment_amount - interest_payment
        balance -= principal_payment
        if balance < 0:
            principal_payment += balance
            balance = 0
            payment_list.append(principal_payment + interest_payment)
            interest_list.append(interest_payment)
            principal_list.append(principal_payment)
            break
        payment_list.append(payment_amount)
        interest_list.append(interest_payment)
        principal_list.append(principal_payment)
    
    return np.array(payment_list), np.array(interest_list), np.array(principal_list)

# Main calculation function
def calculate_investment_outlook(params):
    property_value = params['property_value']
    loan_amount = params['loan_amount']
    interest_rate = params['interest_rate']
    loan_term = params['loan_term']
    payment_frequency = params['payment_frequency']
    annual_salary = params['annual_salary']
    marginal_tax_rate = params['marginal_tax_rate']
    weekly_rental_income = params['weekly_rental_income']
    annual_rental_increase = params['annual_rental_increase']
    annual_expense_increase = params['annual_expense_increase']
    property_appreciation = params['property_appreciation']
    council_rates = params['council_rates']
    water_rates = params['water_rates']
    land_tax = params['land_tax']
    strata_fees = params['strata_fees']
    insurance = params['insurance']
    property_manager_rate = params['property_manager_rate']
    repairs_and_maintenance = params['repairs_and_maintenance']
    depreciation = params['depreciation']
    
    initial_mortgage_payment = calculate_mortgage_payment(
        loan_amount, interest_rate, loan_term, payment_frequency
    )
    
    payments, interests, principals = generate_amortization_schedule(
        loan_amount, interest_rate, loan_term, payment_frequency, initial_mortgage_payment
    )
    
    years = np.arange(1, loan_term + 1)
    annual_interest = np.array([np.sum(interests[i * payment_frequency:(i + 1) * payment_frequency]) for i in range(loan_term)])
    annual_principal = np.array([np.sum(principals[i * payment_frequency:(i + 1) * payment_frequency]) for i in range(loan_term)])
    annual_rental_income_array = np.array([weekly_rental_income * 52 * ((1 + annual_rental_increase) ** i) for i in range(loan_term)])
    
    property_manager_fees = property_manager_rate * annual_rental_income_array
    total_annual_expenses = (
        annual_interest +
        council_rates * (1 + annual_expense_increase) ** years +
        water_rates * (1 + annual_expense_increase) ** years +
        land_tax +
        strata_fees * (1 + annual_expense_increase) ** years +
        insurance * (1 + annual_expense_increase) ** years +
        property_manager_fees +
        repairs_and_maintenance +
        depreciation
    )
    
    net_rental_loss = annual_rental_income_array - total_annual_expenses
    tax_benefit = -net_rental_loss * marginal_tax_rate
    net_profit_loss_after_tax = net_rental_loss + tax_benefit
    
    property_values = property_value * (1 + property_appreciation) ** np.arange(loan_term + 1)
    capital_gains = np.diff(property_values)
    
    final_net_gain_loss = net_profit_loss_after_tax + capital_gains[:loan_term]
    
    results = pd.DataFrame({
        'Year': years,
        'Rental Income': annual_rental_income_array,
        'Interest Payment': annual_interest,
        'Principal Payment': annual_principal,
        'Total Expenses + Depreciation': total_annual_expenses,
        'Net Rental Loss': net_rental_loss,
        'Tax Benefit': tax_benefit,
        'Cashflow after Negative Gearing': net_profit_loss_after_tax,
        'Capital Gains': capital_gains[:loan_term],
        'Final Net Gain/Loss': final_net_gain_loss
    })
    
    return results

# Streamlit UI components
st.title('Investment Outlook Calculator')

# Define user inputs
property_value = st.number_input('Property Value:', value=500000.0)
loan_amount = st.number_input('Loan Amount:', value=450000.0)
interest_rate = st.number_input('Interest Rate:', value=0.0625)
loan_term = st.number_input('Loan Term (years):', value=30)
payment_frequency = st.number_input('Payment Frequency (per year):', value=52)
annual_salary = st.number_input('Annual Salary:', value=93600.0)
marginal_tax_rate = st.number_input('Marginal Tax Rate:', value=0.32)
weekly_rental_income = st.number_input('Weekly Rental Income:', value=400.0)
annual_rental_increase = st.number_input('Annual Rental Increase:', value=0.02)
annual_expense_increase = st.number_input('Annual Expense Increase:', value=0.02)
property_appreciation = st.number_input('Property Appreciation:', value=0.04)
council_rates = st.number_input('Council Rates:', value=700.0)
water_rates = st.number_input('Water Rates:', value=550.0)
land_tax = st.number_input('Land Tax:', value=0.0)
strata_fees = st.number_input('Strata Fees:', value=500.0)
insurance = st.number_input('Insurance:', value=1250.0)
property_manager_rate = st.number_input('Property Manager Rate:', value=0.07)
repairs_and_maintenance = st.number_input('Repairs and Maintenance:', value=2000.0)
depreciation = st.number_input('Depreciation:', value=7500.0)



# (Rest of your code remains the same)

# Main Streamlit App Logic
if st.button('Run Calculations'):
    params = {
        'property_value': property_value,
        'loan_amount': loan_amount,
        'interest_rate': interest_rate,
        'loan_term': loan_term,
        'payment_frequency': payment_frequency,
        'annual_salary': annual_salary,
        'marginal_tax_rate': marginal_tax_rate,
        'weekly_rental_income': weekly_rental_income,
        'annual_rental_increase': annual_rental_increase,
        'annual_expense_increase': annual_expense_increase,
        'property_appreciation': property_appreciation,
        'council_rates': council_rates,
        'water_rates': water_rates,
        'land_tax': land_tax,
        'strata_fees': strata_fees,
        'insurance': insurance,
        'property_manager_rate': property_manager_rate,
        'repairs_and_maintenance': repairs_and_maintenance,
        'depreciation': depreciation
    }
    
    results = calculate_investment_outlook(params)
    
    # Display the results
    st.dataframe(results)

    # Create a buffer to save the Excel file
    excel_buffer = BytesIO()

    # Save the DataFrame to the Excel buffer
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        results.to_excel(writer, index=False)

    excel_buffer.seek(0)  # Set the buffer's position to the beginning

    # Create a download button
    st.download_button(
        label="Download Excel",
        data=excel_buffer,
        file_name="investment_outlook.xlsx",
        mime="application/vnd.ms-excel"
    )