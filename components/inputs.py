"""Input components for the Streamlit mortgage calculator."""

import streamlit as st
from config.settings import DEFAULT_VALUES
from utils.formatters import format_currency, format_percentage


def render_sidebar():
    """Render all input controls in the sidebar."""
    with st.sidebar:
        st.header("🏠 Mortgage Calculator")
        
        # Loan details
        loan_amount, loan_years = render_loan_inputs()
        
        # Interest rates
        render_interest_rates()
        
        # Payment settings
        min_payment, additional_payment = render_payment_inputs()
        
        # Refinancing options
        refinance, refinance_cycle, refinance_threshold, rate_increase = render_refinancing_inputs()
        
        # Store values in session state
        st.session_state.loan_amount = loan_amount
        st.session_state.loan_years = loan_years
        st.session_state.min_payment = min_payment
        st.session_state.additional_payment = additional_payment
        st.session_state.refinance = refinance
        st.session_state.refinance_cycle = refinance_cycle
        st.session_state.refinance_threshold = refinance_threshold
        st.session_state.rate_increase = rate_increase


def render_loan_inputs():
    """Render loan amount and term inputs."""
    st.subheader("💰 Loan Details")
    
    # Loan amount with both slider and number input
    loan_amount = st.number_input(
        "Loan Amount ($)",
        min_value=10000,
        max_value=10000000,
        value=st.session_state.get('loan_amount', DEFAULT_VALUES['loan_amount']),
        step=10000,
        format="%d",
        key="loan_amount_input"
    )
    
    # Loan amount slider for visual adjustment
    loan_amount_slider = st.slider(
        "Adjust Loan Amount",
        min_value=10000,
        max_value=10000000,
        value=loan_amount,
        step=10000,
        format="$%d",
        key="loan_amount_slider"
    )
    
    # Sync slider and input
    if loan_amount != loan_amount_slider:
        loan_amount = loan_amount_slider
    
    # Loan term
    loan_years = st.slider(
        "Loan Term (Years)",
        min_value=5,
        max_value=50,
        value=st.session_state.get('loan_years', DEFAULT_VALUES['years']),
        step=1,
        key="loan_years_input"
    )
    
    return loan_amount, loan_years


def render_interest_rates():
    """Render dynamic interest rate inputs."""
    st.subheader("📈 Interest Rates")
    
    # Initialize interest rates if not in session state
    if 'interest_rates' not in st.session_state:
        st.session_state.interest_rates = DEFAULT_VALUES['interest_rates'].copy()
    
    # Help text
    st.caption("Add interest rates for each period of your loan")
    
    # Add new rate
    col1, col2 = st.columns([3, 1])
    with col1:
        new_rate = st.number_input(
            "New Rate (%)",
            min_value=0.1,
            max_value=20.0,
            value=3.0,
            step=0.1,
            format="%.1f",
            label_visibility="collapsed"
        )
    with col2:
        if st.button("➕ Add", use_container_width=True):
            st.session_state.interest_rates.append(new_rate)
            st.rerun()
    
    # Display current rates
    if st.session_state.interest_rates:
        st.write("**Current Rates:**")
        
        # Create a container for rates
        rates_container = st.container()
        
        with rates_container:
            for i, rate in enumerate(st.session_state.interest_rates):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.caption(f"Period {i+1}")
                
                with col2:
                    updated_rate = st.number_input(
                        f"Rate {i+1}",
                        min_value=0.1,
                        max_value=20.0,
                        value=rate,
                        step=0.1,
                        format="%.1f",
                        key=f"rate_{i}",
                        label_visibility="collapsed"
                    )
                    st.session_state.interest_rates[i] = updated_rate
                
                with col3:
                    if st.button("🗑️", key=f"remove_{i}", use_container_width=True):
                        st.session_state.interest_rates.pop(i)
                        st.rerun()
    else:
        st.warning("Please add at least one interest rate")


def render_payment_inputs():
    """Render payment settings inputs."""
    st.subheader("💳 Payment Settings")
    
    min_payment = st.number_input(
        "Minimum Monthly Payment ($)",
        min_value=0,
        value=st.session_state.get('min_payment', DEFAULT_VALUES['minimum_monthly_payment']),
        step=100,
        format="%d",
        help="Set a minimum payment amount if required by your loan terms"
    )
    
    additional_payment = st.number_input(
        "Additional Monthly Payment ($)",
        min_value=0,
        value=st.session_state.get('additional_payment', DEFAULT_VALUES['additional_payment']),
        step=100,
        format="%d",
        help="Extra payment to reduce principal faster"
    )
    
    # Show impact preview
    if additional_payment > 0:
        st.info(f"💡 Making ${additional_payment:,} extra payments monthly")
    
    return min_payment, additional_payment


def render_refinancing_inputs():
    """Render refinancing options."""
    with st.expander("🔄 Refinancing Options", expanded=False):
        refinance = st.checkbox(
            "Enable Refinancing Analysis",
            value=st.session_state.get('refinance', DEFAULT_VALUES['refinance']),
            help="Model the impact of refinancing your loan"
        )
        
        if refinance:
            col1, col2 = st.columns(2)
            
            with col1:
                refinance_cycle = st.number_input(
                    "Refinance Every (Years)",
                    min_value=1,
                    max_value=10,
                    value=st.session_state.get('refinance_cycle', DEFAULT_VALUES['refinance_every_x_years']),
                    help="How often to consider refinancing"
                )
                
                refinance_threshold = st.number_input(
                    "Principal Threshold ($)",
                    min_value=100000,
                    max_value=10000000,
                    value=st.session_state.get('refinance_threshold', DEFAULT_VALUES['refinance_when_principal_hit']),
                    step=100000,
                    format="%d",
                    help="Refinance when principal drops to this amount"
                )
            
            with col2:
                rate_increase = st.number_input(
                    "Rate Increase After Refinance (%)",
                    min_value=0.0,
                    max_value=5.0,
                    value=st.session_state.get('rate_increase', DEFAULT_VALUES['refinance_interest_will_increase']),
                    step=0.1,
                    format="%.1f",
                    help="Expected rate increase when refinancing"
                )
                
                # Preview
                st.caption(f"New rate will be current + {rate_increase}%")
            
            return refinance, refinance_cycle, refinance_threshold, rate_increase
        
        return False, 3, 3000000, 1.0 