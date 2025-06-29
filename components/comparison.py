"""Comparison component for multi-scenario analysis."""

import streamlit as st
import pandas as pd
from logic import calculate_monthly_payment
from utils.helpers import calculate_summary_metrics
from utils.formatters import format_currency, format_years_months, format_percentage
from components.charts import render_comparison_chart, render_comparison_metrics_chart


def render_comparison():
    """Render the comparison view for multiple scenarios."""
    st.title("🔄 Scenario Comparison")
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.comparison_mode = False
        st.rerun()
    
    if not st.session_state.get('scenarios') or len(st.session_state.scenarios) < 2:
        st.warning("⚠️ Please save at least 2 scenarios to compare them.")
        st.info("Go back to the dashboard and save different mortgage configurations as scenarios.")
        return
    
    # Scenario selection
    st.subheader("Select Scenarios to Compare")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_scenarios = st.multiselect(
            "Choose 2-4 scenarios",
            options=list(st.session_state.scenarios.keys()),
            default=list(st.session_state.scenarios.keys())[:4],
            max_selections=4,
            help="Select between 2 and 4 scenarios to compare"
        )
    
    with col2:
        if st.button("🔄 Refresh Comparison", use_container_width=True):
            st.rerun()
    
    if len(selected_scenarios) < 2:
        st.error("Please select at least 2 scenarios to compare.")
        return
    
    # Calculate results for selected scenarios
    comparison_results = {}
    comparison_metrics = {}
    
    with st.spinner("Calculating scenarios..."):
        for scenario_name in selected_scenarios:
            params = st.session_state.scenarios[scenario_name]
            try:
                result = calculate_monthly_payment(**params)
                result_df = pd.DataFrame(result)
                comparison_results[scenario_name] = result_df
                comparison_metrics[scenario_name] = calculate_summary_metrics(result_df)
            except Exception as e:
                st.error(f"Error calculating scenario '{scenario_name}': {str(e)}")
                return
    
    # Display comparison
    render_comparison_summary(comparison_metrics)
    
    st.markdown("---")
    
    # Charts
    render_comparison_charts_section(comparison_results, comparison_metrics)
    
    st.markdown("---")
    
    # Detailed comparison table
    render_comparison_table(comparison_metrics, selected_scenarios)
    
    st.markdown("---")
    
    # Recommendations
    render_recommendations(comparison_metrics)


def render_comparison_summary(comparison_metrics: dict):
    """Render summary cards comparing key metrics."""
    st.subheader("📊 Quick Comparison")
    
    # Find best scenarios
    min_interest = min(comparison_metrics.items(), key=lambda x: x[1]['total_interest'])
    min_time = min(comparison_metrics.items(), key=lambda x: x[1]['total_months'])
    min_total = min(comparison_metrics.items(), key=lambda x: x[1]['total_paid'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success(f"""
        **Lowest Interest**  
        🏆 {min_interest[0]}  
        {format_currency(min_interest[1]['total_interest'])}
        """)
    
    with col2:
        st.info(f"""
        **Fastest Payoff**  
        🏆 {min_time[0]}  
        {format_years_months(min_time[1]['total_months'])}
        """)
    
    with col3:
        st.warning(f"""
        **Lowest Total Cost**  
        🏆 {min_total[0]}  
        {format_currency(min_total[1]['total_paid'])}
        """)


def render_comparison_charts_section(comparison_results: dict, comparison_metrics: dict):
    """Render comparison charts."""
    st.subheader("📈 Visual Comparison")
    
    tab1, tab2, tab3 = st.tabs(["Loan Balance", "Key Metrics", "Payment Schedule"])
    
    with tab1:
        fig = render_comparison_chart(comparison_results)
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight
        st.caption("💡 This chart shows how the loan balance decreases over time for each scenario.")
    
    with tab2:
        fig = render_comparison_metrics_chart(comparison_metrics)
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insight
        st.caption("💡 Compare total interest, total paid, and payoff time across scenarios.")
    
    with tab3:
        render_payment_schedule_comparison(comparison_results)


def render_payment_schedule_comparison(comparison_results: dict):
    """Render payment schedule comparison."""
    # Get first 12 months for each scenario
    comparison_data = []
    
    for scenario_name, result_df in comparison_results.items():
        for month in range(min(12, len(result_df))):
            row = result_df.iloc[month]
            comparison_data.append({
                'Scenario': scenario_name,
                'Month': month + 1,
                'Total Payment': row['total'],
                'Principal': row['principal'],
                'Interest': row['interest'],
                'Balance': row['loan_end']
            })
    
    df = pd.DataFrame(comparison_data)
    
    # Pivot for better comparison
    pivot_df = df.pivot_table(
        index='Month',
        columns='Scenario',
        values=['Total Payment', 'Balance'],
        aggfunc='first'
    )
    
    # Flatten column names
    pivot_df.columns = [f'{col[1]} - {col[0]}' for col in pivot_df.columns]
    
    st.write("**First Year Payment Comparison**")
    
    # Format currency columns for display
    display_df = pivot_df.reset_index()
    for col in pivot_df.columns:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "")
    
    # Display using Streamlit's native dataframe
    st.dataframe(
        display_df,
        height=300,
        use_container_width=True,
        hide_index=True
    )


def render_comparison_table(comparison_metrics: dict, selected_scenarios: list):
    """Render detailed comparison table."""
    st.subheader("📋 Detailed Comparison")
    
    # Create comparison dataframe
    data = []
    for scenario in selected_scenarios:
        metrics = comparison_metrics[scenario]
        params = st.session_state.scenarios[scenario]
        
        data.append({
            'Scenario': scenario,
            'Loan Amount': format_currency(params['loan']),
            'Term (Years)': params['years'],
            'Interest Rates': ', '.join([f"{r}%" for r in params['interest_rates_100']]),
            'Additional Payment': format_currency(params['additional_payment']),
            'Payoff Time': format_years_months(metrics['total_months']),
            'Total Interest': format_currency(metrics['total_interest']),
            'Total Paid': format_currency(metrics['total_paid']),
            'Avg Monthly': format_currency(metrics['avg_monthly']),
            'Interest %': format_percentage(metrics['interest_percentage'])
        })
    
    df = pd.DataFrame(data)
    
    # Display using Streamlit's native dataframe
    st.dataframe(
        df,
        height=200,
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Comparison",
        data=csv,
        file_name="scenario_comparison.csv",
        mime="text/csv"
    )


def render_recommendations(comparison_metrics: dict):
    """Render recommendations based on comparison."""
    st.subheader("💡 Recommendations")
    
    # Find best scenarios for different priorities
    scenarios = list(comparison_metrics.keys())
    
    # Calculate savings between scenarios
    if len(scenarios) >= 2:
        # Sort by total interest
        sorted_by_interest = sorted(
            comparison_metrics.items(),
            key=lambda x: x[1]['total_interest']
        )
        
        best_scenario = sorted_by_interest[0]
        worst_scenario = sorted_by_interest[-1]
        
        interest_savings = worst_scenario[1]['total_interest'] - best_scenario[1]['total_interest']
        time_difference = worst_scenario[1]['total_months'] - best_scenario[1]['total_months']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"""
            **Best Overall: {best_scenario[0]}**
            - Saves {format_currency(interest_savings)} in interest
            - Pays off {abs(time_difference)} months {'faster' if time_difference > 0 else 'slower'}
            - Total cost: {format_currency(best_scenario[1]['total_paid'])}
            """)
        
        with col2:
            # Find balanced option
            avg_interest = sum(m['total_interest'] for _, m in comparison_metrics.items()) / len(comparison_metrics)
            balanced = min(
                comparison_metrics.items(),
                key=lambda x: abs(x[1]['total_interest'] - avg_interest)
            )
            
            st.info(f"""
            **Balanced Option: {balanced[0]}**
            - Moderate interest: {format_currency(balanced[1]['total_interest'])}
            - Payoff time: {format_years_months(balanced[1]['total_months'])}
            - Good compromise between cost and time
            """)
    
    # Additional insights
    with st.expander("📊 Additional Insights", expanded=True):
        insights = generate_insights(comparison_metrics)
        for insight in insights:
            st.write(f"• {insight}")


def generate_insights(comparison_metrics: dict) -> list:
    """Generate insights from comparison metrics."""
    insights = []
    
    if len(comparison_metrics) < 2:
        return insights
    
    # Interest rate impact
    interest_range = max(m['total_interest'] for _, m in comparison_metrics.items()) - \
                    min(m['total_interest'] for _, m in comparison_metrics.items())
    
    if interest_range > 0:
        insights.append(
            f"Interest costs vary by {format_currency(interest_range)} across scenarios, "
            f"highlighting the importance of rate shopping and payment strategies."
        )
    
    # Time impact
    time_range = max(m['total_months'] for _, m in comparison_metrics.items()) - \
                min(m['total_months'] for _, m in comparison_metrics.items())
    
    if time_range > 0:
        insights.append(
            f"Payoff times differ by {time_range} months ({time_range/12:.1f} years), "
            f"showing how payment strategies affect loan duration."
        )
    
    # Additional payment impact
    scenarios_with_extra = [
        name for name, _ in comparison_metrics.items()
        if st.session_state.scenarios[name]['additional_payment'] > 0
    ]
    
    if scenarios_with_extra:
        insights.append(
            f"Scenarios with additional payments ({', '.join(scenarios_with_extra)}) "
            f"show significant interest savings and faster payoff times."
        )
    
    # Refinancing impact
    scenarios_with_refi = [
        name for name, _ in comparison_metrics.items()
        if st.session_state.scenarios[name]['refinance']
    ]
    
    if scenarios_with_refi:
        insights.append(
            f"Refinancing scenarios ({', '.join(scenarios_with_refi)}) "
            f"should be evaluated based on actual market conditions and fees."
        )
    
    return insights 