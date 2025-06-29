"""Output components for displaying calculation results."""

import streamlit as st
import pandas as pd
from utils.formatters import format_currency, format_years_months, format_percentage
from utils.helpers import calculate_summary_metrics, create_annual_summary
from components.charts import render_payment_timeline, render_loan_balance_chart, render_interest_vs_principal_chart
from logic import calculate_monthly_payment


def render_dashboard():
    """Render the main dashboard with calculation results."""
    # Get current parameters
    from utils.helpers import get_current_parameters, validate_inputs, params_changed
    
    params = get_current_parameters()
    
    # Validate inputs
    is_valid, error_msg = validate_inputs(params)
    
    if not is_valid:
        st.error(f"❌ Invalid inputs: {error_msg}")
        return
    
    # Check if we need to recalculate
    if params_changed(params, st.session_state.get('last_params')):
        with st.spinner("Calculating..."):
            try:
                result = calculate_monthly_payment(**params)
                st.session_state.calculation_result = pd.DataFrame(result)
                st.session_state.last_params = params.copy()
            except Exception as e:
                st.error(f"❌ Calculation error: {str(e)}")
                return
    
    if st.session_state.calculation_result is None:
        st.info("👈 Please configure your mortgage parameters in the sidebar")
        return
    
    # Display results
    result_df = st.session_state.calculation_result
    
    # Title
    st.title("🏠 Mortgage Analysis Dashboard")
    
    # Key metrics
    render_metrics_cards(result_df)
    
    # Charts section
    st.markdown("---")
    render_charts_section(result_df)
    
    # Data tables section
    st.markdown("---")
    render_data_tables_section(result_df)
    
    # Scenario comparison
    st.markdown("---")
    render_scenario_section()


def render_metrics_cards(calculation_result: pd.DataFrame):
    """Display key metrics in card format."""
    metrics = calculate_summary_metrics(calculation_result)
    
    st.subheader("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Payoff Time",
            value=format_years_months(metrics['total_months']),
            delta=None,
            help="Total time to pay off the loan"
        )
    
    with col2:
        st.metric(
            label="Total Interest",
            value=format_currency(metrics['total_interest']),
            delta=f"{metrics['interest_percentage']:.1f}% of total",
            delta_color="normal",
            help="Total interest paid over the loan term"
        )
    
    with col3:
        st.metric(
            label="Total Paid",
            value=format_currency(metrics['total_paid']),
            delta=None,
            help="Total amount paid (principal + interest)"
        )
    
    with col4:
        st.metric(
            label="Avg Monthly Payment",
            value=format_currency(metrics['avg_monthly']),
            delta=None,
            help="Average monthly payment over the loan term"
        )
    
    # Additional insights
    with st.expander("💡 Quick Insights", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Principal:** {format_currency(metrics['total_principal'])}  
            **Interest:** {format_currency(metrics['total_interest'])}  
            **Interest Rate:** {metrics['interest_percentage']:.1f}% of total
            """)
        
        with col2:
            # Calculate savings from additional payments
            if st.session_state.get('additional_payment', 0) > 0:
                # Quick approximation of savings
                monthly_extra = st.session_state.additional_payment
                total_extra = monthly_extra * metrics['total_months']
                st.success(f"""
                **Extra Payments Impact:**  
                Monthly Extra: {format_currency(monthly_extra)}  
                Total Extra: {format_currency(total_extra)}  
                """)


def render_charts_section(calculation_result: pd.DataFrame):
    """Render the charts section with tabs."""
    st.subheader("📈 Visualizations")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Payment Timeline", "Loan Balance", "Interest vs Principal", "Annual Summary"])
    
    with tab1:
        fig = render_payment_timeline(calculation_result)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = render_loan_balance_chart(calculation_result)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = render_interest_vs_principal_chart(calculation_result)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        annual_df = create_annual_summary(calculation_result)
        render_annual_summary_chart(annual_df)


def render_annual_summary_chart(annual_summary: pd.DataFrame):
    """Render annual summary bar chart."""
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    # Add principal bars
    fig.add_trace(go.Bar(
        x=annual_summary['Year'],
        y=annual_summary['principal'],
        name='Principal',
        marker_color='#10b981',
        text=annual_summary['principal'].apply(lambda x: f"${x:,.0f}"),
        textposition='auto',
    ))
    
    # Add interest bars
    fig.add_trace(go.Bar(
        x=annual_summary['Year'],
        y=annual_summary['interest'],
        name='Interest',
        marker_color='#ef4444',
        text=annual_summary['interest'].apply(lambda x: f"${x:,.0f}"),
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Annual Payment Breakdown",
        xaxis_title="Year",
        yaxis_title="Amount ($)",
        barmode='stack',
        hovermode='x unified',
        template='plotly_white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_data_tables_section(calculation_result: pd.DataFrame):
    """Render data tables section."""
    st.subheader("📋 Detailed Data")
    
    tab1, tab2 = st.tabs(["Amortization Schedule", "Annual Summary"])
    
    with tab1:
        render_amortization_table(calculation_result)
    
    with tab2:
        annual_df = create_annual_summary(calculation_result)
        render_annual_summary_table(annual_df)


def render_amortization_table(calculation_result: pd.DataFrame):
    """Display the amortization schedule."""
    # Prepare the dataframe
    df = calculation_result.copy()
    df['Month'] = range(1, len(df) + 1)
    df['Year'] = ((df['Month'] - 1) // 12) + 1
    df['Month_in_Year'] = ((df['Month'] - 1) % 12) + 1
    
    # Select and reorder columns
    df = df[['Year', 'Month_in_Year', 'loan_start', 'total', 'principal', 'interest', 'loan_end']]
    
    # Rename columns for display
    df.columns = ['Year', 'Month', 'Starting Balance', 'Total Payment', 'Principal', 'Interest', 'Ending Balance']
    
    # Format currency columns for display
    display_df = df.copy()
    currency_columns = ['Starting Balance', 'Total Payment', 'Principal', 'Interest', 'Ending Balance']
    for col in currency_columns:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
    
    # Display using Streamlit's native dataframe with pagination
    st.dataframe(
        display_df,
        height=400,
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Amortization Schedule",
        data=csv,
        file_name="amortization_schedule.csv",
        mime="text/csv"
    )


def render_annual_summary_table(annual_summary: pd.DataFrame):
    """Display annual summary table."""
    # Format the dataframe for display
    display_df = annual_summary.copy()
    
    # Format currency columns
    currency_cols = ['principal', 'interest', 'total', 'loan_end', 'cumulative_interest', 'cumulative_principal']
    for col in currency_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: format_currency(x))
    
    # Rename columns for display
    display_df.columns = [
        'Year', 'Principal Paid', 'Interest Paid', 'Total Paid', 
        'Remaining Balance', 'Cumulative Interest', 'Cumulative Principal'
    ]
    
    # Display using Streamlit's native dataframe
    st.dataframe(
        display_df,
        height=400,
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Annual Summary",
        data=csv,
        file_name="annual_summary.csv",
        mime="text/csv"
    )


def render_scenario_section():
    """Render scenario management section."""
    st.subheader("🔍 Scenario Management")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        scenario_name = st.text_input(
            "Scenario Name",
            placeholder="e.g., Conservative, Aggressive, With Extra Payments",
            key="scenario_name_input"
        )
    
    with col2:
        if st.button("💾 Save Current Scenario", use_container_width=True, type="primary"):
            if scenario_name:
                from utils.helpers import get_current_parameters
                current_params = get_current_parameters()
                
                if 'scenarios' not in st.session_state:
                    st.session_state.scenarios = {}
                
                st.session_state.scenarios[scenario_name] = current_params
                st.success(f"✅ Saved scenario: {scenario_name}")
                st.session_state.current_scenario_name = scenario_name
            else:
                st.error("Please enter a scenario name")
    
    with col3:
        if st.button("🔄 Compare Scenarios", use_container_width=True):
            st.session_state.comparison_mode = True
            st.rerun()
    
    # Display saved scenarios
    if st.session_state.get('scenarios'):
        st.write("**Saved Scenarios:**")
        
        for name in st.session_state.scenarios:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                if name == st.session_state.get('current_scenario_name'):
                    st.write(f"✅ **{name}** (current)")
                else:
                    st.write(f"📌 {name}")
            
            with col2:
                if st.button("Load", key=f"load_{name}", use_container_width=True):
                    from utils.helpers import load_scenario
                    load_scenario(st.session_state.scenarios[name])
                    st.session_state.current_scenario_name = name
                    st.rerun()
            
            with col3:
                if st.button("🗑️", key=f"delete_{name}", use_container_width=True):
                    del st.session_state.scenarios[name]
                    if st.session_state.get('current_scenario_name') == name:
                        st.session_state.current_scenario_name = None
                    st.rerun() 