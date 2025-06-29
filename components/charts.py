"""Chart components for visualizing mortgage data."""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from config.settings import COLORS


def render_payment_timeline(calculation_result: pd.DataFrame):
    """Create payment timeline chart showing principal vs interest over time."""
    df = calculation_result.copy()
    df['Month'] = range(1, len(df) + 1)
    
    fig = go.Figure()
    
    # Interest payments (bottom layer)
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['interest'],
        mode='lines',
        name='Interest',
        fill='tozeroy',
        fillcolor=f'rgba(239, 68, 68, 0.3)',
        line=dict(color='#ef4444', width=2),
        hovertemplate='Month %{x}<br>Interest: $%{y:,.0f}<extra></extra>'
    ))
    
    # Total payments (principal + interest)
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['total'],
        mode='lines',
        name='Total Payment',
        fill='tonexty',
        fillcolor=f'rgba(16, 185, 129, 0.3)',
        line=dict(color='#10b981', width=2),
        hovertemplate='Month %{x}<br>Total: $%{y:,.0f}<extra></extra>'
    ))
    
    # Add principal as invisible trace for hover info
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['principal'],
        mode='lines',
        name='Principal',
        line=dict(color='rgba(0,0,0,0)'),
        showlegend=False,
        hovertemplate='Month %{x}<br>Principal: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': "Monthly Payment Breakdown Over Time",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Month",
        yaxis_title="Payment Amount ($)",
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Add vertical lines for year markers
    years = len(df) // 12
    for year in range(1, years + 1):
        fig.add_vline(
            x=year * 12,
            line_dash="dot",
            line_color="gray",
            opacity=0.3,
            annotation_text=f"Year {year}"
        )
    
    return fig


def render_loan_balance_chart(calculation_result: pd.DataFrame):
    """Create loan balance chart showing remaining balance over time."""
    df = calculation_result.copy()
    df['Month'] = range(1, len(df) + 1)
    
    fig = go.Figure()
    
    # Main balance line
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['loan_end'],
        mode='lines',
        name='Remaining Balance',
        line=dict(color=COLORS['primary'], width=3),
        fill='tozeroy',
        fillcolor=f'rgba(30, 58, 138, 0.1)',
        hovertemplate='Month %{x}<br>Balance: $%{y:,.0f}<extra></extra>'
    ))
    
    # Add markers for refinancing points if applicable
    if 'refinanced' in df.columns:
        refinance_points = df[df['refinanced'] == True]
        if not refinance_points.empty:
            fig.add_trace(go.Scatter(
                x=refinance_points['Month'],
                y=refinance_points['loan_end'],
                mode='markers',
                name='Refinance Points',
                marker=dict(
                    color=COLORS['accent'],
                    size=10,
                    symbol='diamond'
                ),
                hovertemplate='Refinanced<br>Month %{x}<br>Balance: $%{y:,.0f}<extra></extra>'
            ))
    
    fig.update_layout(
        title={
            'text': "Loan Balance Over Time",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Month",
        yaxis_title="Remaining Balance ($)",
        template='plotly_white',
        height=500,
        hovermode='x unified',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Add horizontal line at 50% of initial loan
    initial_loan = df['loan_start'].iloc[0]
    fig.add_hline(
        y=initial_loan * 0.5,
        line_dash="dash",
        line_color="gray",
        opacity=0.5,
        annotation_text="50% of Original Loan"
    )
    
    return fig


def render_interest_vs_principal_chart(calculation_result: pd.DataFrame):
    """Create a chart comparing cumulative interest vs principal payments."""
    df = calculation_result.copy()
    df['Month'] = range(1, len(df) + 1)
    df['cumulative_principal'] = df['principal'].cumsum()
    df['cumulative_interest'] = df['interest'].cumsum()
    
    fig = go.Figure()
    
    # Cumulative principal
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['cumulative_principal'],
        mode='lines',
        name='Cumulative Principal',
        line=dict(color=COLORS['secondary'], width=3),
        hovertemplate='Month %{x}<br>Total Principal: $%{y:,.0f}<extra></extra>'
    ))
    
    # Cumulative interest
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['cumulative_interest'],
        mode='lines',
        name='Cumulative Interest',
        line=dict(color=COLORS['error'], width=3),
        hovertemplate='Month %{x}<br>Total Interest: $%{y:,.0f}<extra></extra>'
    ))
    
    # Add total paid line
    df['cumulative_total'] = df['total'].cumsum()
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['cumulative_total'],
        mode='lines',
        name='Total Paid',
        line=dict(color=COLORS['primary'], width=2, dash='dash'),
        hovertemplate='Month %{x}<br>Total Paid: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': "Cumulative Principal vs Interest Payments",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Month",
        yaxis_title="Cumulative Amount ($)",
        template='plotly_white',
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def render_comparison_chart(comparison_results: dict):
    """Create a comparison chart for multiple scenarios."""
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set2
    
    for i, (scenario_name, result_df) in enumerate(comparison_results.items()):
        df = result_df.copy()
        df['Month'] = range(1, len(df) + 1)
        
        # Add loan balance line for each scenario
        fig.add_trace(go.Scatter(
            x=df['Month'],
            y=df['loan_end'],
            mode='lines',
            name=f'{scenario_name}',
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate=f'{scenario_name}<br>Month %{{x}}<br>Balance: $%{{y:,.0f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title={
            'text': "Scenario Comparison - Loan Balance",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Month",
        yaxis_title="Remaining Balance ($)",
        template='plotly_white',
        height=500,
        hovermode='x unified',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def render_comparison_metrics_chart(comparison_metrics: dict):
    """Create a bar chart comparing key metrics across scenarios."""
    # Prepare data
    scenarios = list(comparison_metrics.keys())
    metrics_data = {
        'Total Interest': [],
        'Total Paid': [],
        'Payoff Months': []
    }
    
    for scenario in scenarios:
        metrics = comparison_metrics[scenario]
        metrics_data['Total Interest'].append(metrics['total_interest'])
        metrics_data['Total Paid'].append(metrics['total_paid'])
        metrics_data['Payoff Months'].append(metrics['total_months'])
    
    # Create subplots
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Total Interest', 'Total Paid', 'Payoff Time (Months)'),
        horizontal_spacing=0.1
    )
    
    colors = px.colors.qualitative.Set2
    
    # Total Interest
    fig.add_trace(
        go.Bar(
            x=scenarios,
            y=metrics_data['Total Interest'],
            name='Total Interest',
            marker_color=colors[0],
            text=[f"${v:,.0f}" for v in metrics_data['Total Interest']],
            textposition='auto'
        ),
        row=1, col=1
    )
    
    # Total Paid
    fig.add_trace(
        go.Bar(
            x=scenarios,
            y=metrics_data['Total Paid'],
            name='Total Paid',
            marker_color=colors[1],
            text=[f"${v:,.0f}" for v in metrics_data['Total Paid']],
            textposition='auto'
        ),
        row=1, col=2
    )
    
    # Payoff Months
    fig.add_trace(
        go.Bar(
            x=scenarios,
            y=metrics_data['Payoff Months'],
            name='Payoff Months',
            marker_color=colors[2],
            text=[f"{v:,.0f}" for v in metrics_data['Payoff Months']],
            textposition='auto'
        ),
        row=1, col=3
    )
    
    fig.update_layout(
        title={
            'text': "Scenario Comparison - Key Metrics",
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=False,
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=100, b=50)
    )
    
    # Update y-axes
    fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
    fig.update_yaxes(title_text="Amount ($)", row=1, col=2)
    fig.update_yaxes(title_text="Months", row=1, col=3)
    
    return fig


def render_interest_rate_sensitivity_chart(base_result: pd.DataFrame, rate_variations: dict):
    """Create a chart showing sensitivity to interest rate changes."""
    fig = go.Figure()
    
    colors = px.colors.sequential.Blues_r
    
    for i, (rate_name, result_df) in enumerate(rate_variations.items()):
        df = result_df.copy()
        total_interest = df['interest'].sum()
        total_months = len(df)
        
        fig.add_trace(go.Scatter(
            x=[rate_name],
            y=[total_interest],
            mode='markers+text',
            name=rate_name,
            marker=dict(
                size=20,
                color=colors[i % len(colors)]
            ),
            text=[f"${total_interest:,.0f}<br>{total_months} months"],
            textposition="top center",
            hovertemplate=f'{rate_name}<br>Total Interest: $%{{y:,.0f}}<br>Months: {total_months}<extra></extra>'
        ))
    
    fig.update_layout(
        title={
            'text': "Interest Rate Sensitivity Analysis",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Interest Rate Scenario",
        yaxis_title="Total Interest Paid ($)",
        template='plotly_white',
        height=400,
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig 