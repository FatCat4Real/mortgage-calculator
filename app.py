import streamlit as st
import pandas as pd
from logic import calculate_monthly_payment

# Configure page settings - must be the first Streamlit command
st.set_page_config(
    page_title="Mortgage Calculator",
    page_icon="🏠",
    layout="wide"
)

def create_scenario_inputs(scenario_id, shared_mode=True, shared_loan=None, shared_years=None):
    inputs = {}
    
    if not shared_mode:
        # Individual mode - show loan amount and years for each scenario
        col1, col2 = st.columns(2)
        with col1:
            inputs['loan'] = st.number_input("Loan Amount", min_value=0.0, value=4_300_000.0, key=f"loan_{scenario_id}")
        with col2:
            inputs['years'] = st.number_input("Years", min_value=1, value=40, key=f"years_{scenario_id}")
    else:
        # Shared mode - use shared values
        inputs['loan'] = shared_loan
        inputs['years'] = shared_years
    
    # Interest rates
    interest_rates_str = st.text_input("Interest Rates", value="2.3,2.9,3.5,4.495,4.495,5.495", key=f"rates_{scenario_id}")
    
    # Additional payments in columns
    col1, col2 = st.columns(2)
    with col1:
        inputs['minimum_monthly_payment'] = st.number_input("Min Monthly", min_value=0.0, value=0.0, key=f"min_payment_{scenario_id}")
    with col2:
        inputs['additional_payment'] = st.number_input("Extra Monthly", min_value=0.0, value=0.0, key=f"add_payment_{scenario_id}")
    
    # Advanced options in columns
    col1, col2 = st.columns(2)  
    with col1:
        inputs['refinance'] = st.checkbox("Refinance", key=f"refinance_{scenario_id}")
        if inputs['refinance']:
            inputs['refinance_every_x_years'] = st.number_input("Every (Y)", min_value=1, value=3, key=f"refinance_years_{scenario_id}")
            inputs['refinance_when_principal_hit'] = st.number_input("When Principal", min_value=0.0, value=3_000_000.0, key=f"refinance_principal_{scenario_id}")
            inputs['refinance_interest_will_increase'] = st.number_input("Rate +", min_value=0.0, value=1.0, key=f"refinance_increase_{scenario_id}")
        else:
            inputs['refinance_every_x_years'] = 3
            inputs['refinance_when_principal_hit'] = 3_000_000
            inputs['refinance_interest_will_increase'] = 1.0

    with col2:
        inputs['topup'] = st.checkbox("Top-up", key=f"topup_{scenario_id}")
        if inputs['topup']:
            inputs['topup_every_x_month'] = st.number_input("Every (M)", min_value=1, value=12, key=f"topup_months_{scenario_id}")
            inputs['topup_amount'] = st.number_input("Amount", min_value=0.0, value=50_000.0, key=f"topup_amount_{scenario_id}")
        else:
            inputs['topup_every_x_month'] = 12
            inputs['topup_amount'] = 50_000.0

    try:
        inputs['interest_rates_100'] = [float(rate.strip()) for rate in interest_rates_str.split(',')]
    except ValueError:
        st.error("Invalid interest rates format")
        inputs['interest_rates_100'] = []

    return inputs

# Compact header
st.title("🏠 Mortgage Calculator")

# Parameter mode selection
parameter_mode = st.radio(
    "📋 Parameter Mode:",
    label_visibility="collapsed",
    options=["Shared loan parameters", "Individual scenario parameters"],
    index=0,
    horizontal=True
)

shared_mode = parameter_mode == "Shared loan parameters"

# Shared parameters section (only show if shared mode is selected)
shared_loan = None
shared_years = None
if shared_mode:
    # st.subheader("🔧 Shared Parameters")
    col1, col2 = st.columns(2)
    with col1:
        shared_loan = st.number_input("Loan Amount", min_value=0.0, value=4_300_000.0, key="shared_loan")
    with col2:
        shared_years = st.number_input("Years", min_value=1, value=40, key="shared_years")
    # st.divider()

if 'scenarios' not in st.session_state:
    st.session_state.scenarios = [1]

# Scenarios in columns
cols = st.columns(len(st.session_state.scenarios))
all_scenario_inputs = []

for i, scenario_id in enumerate(st.session_state.scenarios):
    with cols[i]:
        # Compact scenario header
        col1, col2 = st.columns([0.8, 0.2])
        # col1, col2 = st.columns([0.2, 0.8])
        with col1:
            st.markdown(f"#### Scenario {scenario_id}")
        with col2:
            if len(st.session_state.scenarios) > 1:
                if st.button("✕", key=f"remove_{scenario_id}", type='secondary'):
                    st.session_state.scenarios.remove(scenario_id)
                    st.rerun()

        all_scenario_inputs.append(create_scenario_inputs(scenario_id, shared_mode, shared_loan, shared_years))

# Compact buttons
if st.button("➕ Add Scenario", type='secondary'):
    new_id = 1
    if st.session_state.scenarios:
        new_id = max(st.session_state.scenarios) + 1
    st.session_state.scenarios.append(new_id)
    st.rerun()

calculate = st.button("🧮 Calculate", type="primary")

if calculate:
    results_data = []
    
    for i, scenario_inputs in enumerate(all_scenario_inputs):
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
                    average_per_month = total_paid / len(df)
                else:
                    display_str = "N/A"
                    average_per_month = 0

                results_data.append({
                    "Scenario": i+1,
                    "Total Cost": f"฿{total_paid:,.0f}",
                    "Duration": display_str,
                    "Monthly Avg": f"฿{average_per_month:,.0f}",
                    "Interest": f"฿{total_interest:,.0f}",
                    "total_paid_raw": total_paid,
                    "total_interest_raw": total_interest,
                    "amortization_df": df
                })

            except Exception as e:
                st.error(f"Error in Scenario {i+1}: {e}")
    
    # Compact results
    if results_data:
        st.subheader("📊 Results")
        summary_df = pd.DataFrame(results_data)
        summary_df = summary_df.drop(['total_paid_raw', 'total_interest_raw', 'amortization_df'], axis=1)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # Best scenario details
        if len(results_data) > 1:
            best_idx = min(range(len(results_data)), key=lambda i: results_data[i]['total_paid_raw'])
            best_scenario = results_data[best_idx]
            with st.expander(f"📈 Best Option Details (Scenario {best_scenario['Scenario']})"):
                st.dataframe(best_scenario['amortization_df']) 