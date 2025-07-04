import streamlit as st
import pandas as pd
from logic import calculate_monthly_payment

def create_scenario_inputs(scenario_id):
    inputs = {}
    
    inputs['loan'] = st.number_input("Loan Amount", min_value=0.0, value=4_300_000.0, key=f"loan_{scenario_id}")
    inputs['years'] = st.number_input("Loan Term (Years)", min_value=1, value=40, key=f"years_{scenario_id}")
    
    interest_rates_str = st.text_input("Interest Rates (comma-separated)", value="2.3, 2.9, 3.5, 4.495, 4.495, 5.495", key=f"rates_{scenario_id}")
    
    inputs['minimum_monthly_payment'] = st.number_input("Minimum Monthly Payment", min_value=0.0, value=0.0, key=f"min_payment_{scenario_id}")
    inputs['additional_payment'] = st.number_input("Additional Monthly Payment", min_value=0.0, value=0.0, key=f"add_payment_{scenario_id}")
    
    inputs['refinance'] = st.checkbox("Refinance", key=f"refinance_{scenario_id}")
    if inputs['refinance']:
        inputs['refinance_every_x_years'] = st.number_input("Refinance Every (Years)", min_value=1, value=3, key=f"refinance_years_{scenario_id}")
        inputs['refinance_when_principal_hit'] = st.number_input("Refinance When Principal Hits", min_value=0.0, value=3_000_000.0, key=f"refinance_principal_{scenario_id}")
        inputs['refinance_interest_will_increase'] = st.number_input("Refinance Interest Increase", min_value=0.0, value=1.0, key=f"refinance_increase_{scenario_id}")
    else:
        inputs['refinance_every_x_years'] = 3
        inputs['refinance_when_principal_hit'] = 3_000_000
        inputs['refinance_interest_will_increase'] = 1.0

    inputs['topup'] = st.checkbox("Top-up", key=f"topup_{scenario_id}")
    if inputs['topup']:
        inputs['topup_every_x_month'] = st.number_input("Top-up Every (Months)", min_value=1, value=12, key=f"topup_months_{scenario_id}")
        inputs['topup_amount'] = st.number_input("Top-up Amount", min_value=0.0, value=50_000.0, key=f"topup_amount_{scenario_id}")
    else:
        inputs['topup_every_x_month'] = 12
        inputs['topup_amount'] = 50_000.0

    try:
        inputs['interest_rates_100'] = [float(rate.strip()) for rate in interest_rates_str.split(',')]
    except ValueError:
        st.error("Please enter a valid comma-separated list of numbers for interest rates.")
        inputs['interest_rates_100'] = []

    return inputs

st.title("Mortgage Calculator")

st.markdown("""
This application helps you calculate your mortgage payments and compare different scenarios.
- Use the inputs below to define a scenario.
- Click "Add Scenario" to create another scenario for comparison.
- Click "Calculate" to see the results.
""")

if 'scenarios' not in st.session_state:
    st.session_state.scenarios = [1]

cols = st.columns(len(st.session_state.scenarios))
all_scenario_inputs = []

for i, scenario_id in enumerate(st.session_state.scenarios):
    with cols[i]:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.header(f"Scenario {scenario_id}")
        with col2:
            if len(st.session_state.scenarios) > 1:
                st.write("") # For alignment
                if st.button("❌", key=f"remove_{scenario_id}", help=f"Remove Scenario {scenario_id}"):
                    st.session_state.scenarios.remove(scenario_id)
                    st.rerun()

        all_scenario_inputs.append(create_scenario_inputs(scenario_id))

if st.button("Add Scenario"):
    new_id = 1
    if st.session_state.scenarios:
        new_id = max(st.session_state.scenarios) + 1
    st.session_state.scenarios.append(new_id)
    st.rerun()

if st.button("Calculate"):
    results_cols = st.columns(len(all_scenario_inputs))
    for i, scenario_inputs in enumerate(all_scenario_inputs):
        with results_cols[i]:
            st.header(f"Results for Scenario {i+1}")
            if scenario_inputs['interest_rates_100']:
                try:
                    result = calculate_monthly_payment(**scenario_inputs)
                    df = pd.DataFrame(result)
                    
                    total_paid = df['total'].sum()
                    total_interest = df['interest'].sum()
                    
                    if not df.empty:
                        years_taken = df['year'].max()
                        months_taken = df[df['year'] == years_taken]['month'].max()
                        
                        if months_taken == 12:
                            display_str = f"{years_taken}Y"
                        else:
                            display_years = years_taken - 1
                            if display_years > 0:
                                display_str = f"{display_years}Y {months_taken}M"
                            else:
                                display_str = f"{months_taken}M"
                        st.metric("Loan Period", display_str)
                        average_per_month = total_paid / len(df)
                    else:
                        st.metric("Loan Period", "N/A")
                        average_per_month = 0

                    st.metric("Total Paid", f"฿{total_paid:,.0f}")
                    st.metric("Total Interest Paid", f"฿{total_interest:,.0f}")
                    st.metric("Average Per Month", f"฿{average_per_month:,.0f}")

                    with st.expander("Amortization Schedule"):
                        st.dataframe(df)

                except Exception as e:
                    st.error(f"An error occurred during calculation: {e}") 