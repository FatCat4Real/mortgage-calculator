"""Helper functions for the Streamlit app."""

import streamlit as st
from typing import Dict, Any, List
from config.settings import DEFAULT_VALUES
import pandas as pd


def init_session_state():
    """Initialize session state with default values."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.scenarios = {}
        st.session_state.comparison_mode = False
        st.session_state.current_scenario_name = None
        
        # Initialize interest rates
        if 'interest_rates' not in st.session_state:
            st.session_state.interest_rates = DEFAULT_VALUES['interest_rates'].copy()
        
        # Initialize calculation results
        st.session_state.calculation_result = None
        st.session_state.last_params = None


def get_current_parameters() -> Dict[str, Any]:
    """Get current parameter values from session state."""
    return {
        'loan': st.session_state.get('loan_amount', DEFAULT_VALUES['loan_amount']),
        'years': st.session_state.get('loan_years', DEFAULT_VALUES['years']),
        'interest_rates_100': st.session_state.get('interest_rates', DEFAULT_VALUES['interest_rates']),
        'minimum_monthly_payment': st.session_state.get('min_payment', DEFAULT_VALUES['minimum_monthly_payment']),
        'additional_payment': st.session_state.get('additional_payment', DEFAULT_VALUES['additional_payment']),
        'refinance': st.session_state.get('refinance', DEFAULT_VALUES['refinance']),
        'refinance_every_x_years': st.session_state.get('refinance_cycle', DEFAULT_VALUES['refinance_every_x_years']),
        'refinance_when_principal_hit': st.session_state.get('refinance_threshold', DEFAULT_VALUES['refinance_when_principal_hit']),
        'refinance_interest_will_increase': st.session_state.get('rate_increase', DEFAULT_VALUES['refinance_interest_will_increase'])
    }


def load_scenario(params: Dict[str, Any]):
    """Load scenario parameters into session state."""
    st.session_state.loan_amount = params['loan']
    st.session_state.loan_years = params['years']
    st.session_state.interest_rates = params['interest_rates_100'].copy()
    st.session_state.min_payment = params['minimum_monthly_payment']
    st.session_state.additional_payment = params['additional_payment']
    st.session_state.refinance = params['refinance']
    st.session_state.refinance_cycle = params['refinance_every_x_years']
    st.session_state.refinance_threshold = params['refinance_when_principal_hit']
    st.session_state.rate_increase = params['refinance_interest_will_increase']


def calculate_summary_metrics(calculation_result: pd.DataFrame) -> Dict[str, Any]:
    """Calculate summary metrics from calculation results."""
    total_interest = calculation_result['interest'].sum()
    total_paid = calculation_result['total'].sum()
    total_principal = calculation_result['principal'].sum()
    months_count = len(calculation_result)
    years = months_count // 12
    months = months_count % 12
    avg_monthly = total_paid / months_count if months_count > 0 else 0
    
    return {
        'total_months': months_count,
        'years': years,
        'months': months,
        'total_interest': total_interest,
        'total_paid': total_paid,
        'total_principal': total_principal,
        'avg_monthly': avg_monthly,
        'interest_percentage': (total_interest / total_paid * 100) if total_paid > 0 else 0
    }


def create_annual_summary(calculation_result: pd.DataFrame) -> pd.DataFrame:
    """Create annual summary of payments."""
    df = calculation_result.copy()
    df['Year'] = ((df.index) // 12) + 1
    
    annual_summary = df.groupby('Year').agg({
        'principal': 'sum',
        'interest': 'sum',
        'total': 'sum',
        'loan_end': 'last'
    }).reset_index()
    
    annual_summary['cumulative_interest'] = annual_summary['interest'].cumsum()
    annual_summary['cumulative_principal'] = annual_summary['principal'].cumsum()
    
    return annual_summary


def validate_inputs(params: Dict[str, Any]) -> tuple[bool, str]:
    """Validate input parameters."""
    errors = []
    
    if params['loan'] <= 0:
        errors.append("Loan amount must be greater than 0")
    
    if params['years'] <= 0:
        errors.append("Loan term must be greater than 0")
    
    if not params['interest_rates_100'] or len(params['interest_rates_100']) == 0:
        errors.append("At least one interest rate must be provided")
    
    if any(rate <= 0 for rate in params['interest_rates_100']):
        errors.append("All interest rates must be greater than 0")
    
    if params['minimum_monthly_payment'] < 0:
        errors.append("Minimum monthly payment cannot be negative")
    
    if params['additional_payment'] < 0:
        errors.append("Additional payment cannot be negative")
    
    if params['refinance']:
        if params['refinance_every_x_years'] <= 0:
            errors.append("Refinance cycle must be greater than 0")
        
        if params['refinance_when_principal_hit'] <= 0:
            errors.append("Refinance threshold must be greater than 0")
        
        if params['refinance_interest_will_increase'] < 0:
            errors.append("Rate increase cannot be negative")
    
    if errors:
        return False, "\n".join(errors)
    
    return True, ""


def params_changed(params1: Dict[str, Any], params2: Dict[str, Any]) -> bool:
    """Check if parameters have changed."""
    if params1 is None or params2 is None:
        return True
    
    for key in params1:
        if key == 'interest_rates_100':
            if params1[key] != params2[key]:
                return True
        elif params1[key] != params2.get(key):
            return True
    
    return False 