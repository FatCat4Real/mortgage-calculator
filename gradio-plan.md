# Gradio Mortgage Calculator - Implementation Plan

Based on the core-plan.md, this document provides specific Gradio implementation details.

## Gradio-Specific Implementation

### Framework Setup
- **Framework**: Gradio 4.0+
- **Dependencies**:
  ```
  gradio>=4.0.0
  pandas>=1.5.0
  plotly>=5.0.0
  numpy>=1.24.0
  matplotlib>=3.7.0
  ```
- **Key Features**:
  - Rapid prototyping with minimal code
  - Automatic UI generation from function signatures
  - Built-in sharing and embedding capabilities
  - Live updates and real-time calculations

### Project Structure
```
mortgage_calculator_gradio/
├── app.py                  # Main Gradio application
├── logic.py               # Existing calculation logic (unchanged)
├── components/
│   ├── __init__.py
│   ├── inputs.py          # Input interface definitions
│   ├── outputs.py         # Output formatting functions
│   ├── charts.py          # Chart generation functions
│   └── comparison.py      # Multi-scenario comparison logic
├── utils/
│   ├── __init__.py
│   ├── helpers.py         # Utility functions
│   ├── formatters.py      # Number/currency formatting
│   └── state.py           # State management utilities
└── assets/                # Static assets (CSS, images)
    └── custom.css         # Custom styling
```

## Gradio Implementation Details

### 1. Main Application (app.py)
```python
import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Tuple, List, Dict, Any
from logic import calculate_monthly_payment
from components import charts, outputs, comparison
from utils import formatters, state

# Global state for scenarios
global_state = state.GlobalState()

def mortgage_calculator(
    loan_amount: int,
    years: int,
    interest_rates_str: str,
    minimum_monthly_payment: int,
    additional_payment: int,
    refinance: bool,
    refinance_every_x_years: int,
    refinance_when_principal_hit: int,
    refinance_interest_will_increase: float,
) -> Tuple[str, str, str, str, gr.Plot, gr.Plot, gr.Dataframe]:
    """
    Main calculation function that processes inputs and returns all outputs.
    """
    try:
        # Parse interest rates
        interest_rates = [float(x.strip()) for x in interest_rates_str.split(',') if x.strip()]
        
        if not interest_rates:
            raise ValueError("At least one interest rate is required")
        
        # Perform calculation
        result = calculate_monthly_payment(
            loan=loan_amount,
            years=years,
            interest_rates_100=interest_rates,
            minimum_monthly_payment=minimum_monthly_payment,
            additional_payment=additional_payment,
            refinance=refinance,
            refinance_every_x_years=refinance_every_x_years,
            refinance_when_principal_hit=refinance_when_principal_hit,
            refinance_interest_will_increase=refinance_interest_will_increase,
        )
        
        # Calculate summary metrics
        total_interest = sum(result['interest'])
        total_paid = sum(result['total'])
        months_count = len(result['total'])
        years_taken = months_count // 12
        months_remaining = months_count % 12
        avg_monthly = total_paid / months_count if months_count > 0 else 0
        
        # Format outputs
        payoff_time = f"{years_taken}Y {months_remaining}M"
        total_interest_formatted = formatters.format_currency(total_interest)
        total_paid_formatted = formatters.format_currency(total_paid)
        avg_monthly_formatted = formatters.format_currency(avg_monthly)
        
        # Generate charts
        payment_chart = charts.create_payment_timeline_chart(result)
        balance_chart = charts.create_loan_balance_chart(result)
        
        # Create amortization table
        amortization_df = outputs.create_amortization_dataframe(result)
        
        return (
            payoff_time,
            total_interest_formatted,
            total_paid_formatted,
            avg_monthly_formatted,
            payment_chart,
            balance_chart,
            amortization_df
        )
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        empty_chart = go.Figure()
        empty_df = pd.DataFrame()
        return error_msg, error_msg, error_msg, error_msg, empty_chart, empty_chart, empty_df

def save_scenario(
    scenario_name: str,
    loan_amount: int,
    years: int,
    interest_rates_str: str,
    minimum_monthly_payment: int,
    additional_payment: int,
    refinance: bool,
    refinance_every_x_years: int,
    refinance_when_principal_hit: int,
    refinance_interest_will_increase: float,
) -> str:
    """Save current parameters as a scenario."""
    if not scenario_name.strip():
        return "❌ Please enter a scenario name"
    
    try:
        interest_rates = [float(x.strip()) for x in interest_rates_str.split(',') if x.strip()]
        
        global_state.save_scenario(scenario_name.strip(), {
            'loan_amount': loan_amount,
            'years': years,
            'interest_rates': interest_rates,
            'minimum_monthly_payment': minimum_monthly_payment,
            'additional_payment': additional_payment,
            'refinance': refinance,
            'refinance_every_x_years': refinance_every_x_years,
            'refinance_when_principal_hit': refinance_when_principal_hit,
            'refinance_interest_will_increase': refinance_interest_will_increase,
        })
        
        return f"✅ Scenario '{scenario_name}' saved successfully!"
        
    except Exception as e:
        return f"❌ Error saving scenario: {str(e)}"

def load_scenario(scenario_name: str) -> Tuple:
    """Load a saved scenario and return its parameters."""
    if not scenario_name or scenario_name not in global_state.scenarios:
        # Return default values
        return (
            4300000, 40, "2.3, 2.9, 3.5, 4.495, 4.495, 5.495",
            0, 0, False, 3, 3000000, 1.0,
            "❌ Scenario not found"
        )
    
    try:
        scenario = global_state.scenarios[scenario_name]
        interest_rates_str = ", ".join(map(str, scenario['interest_rates']))
        
        return (
            scenario['loan_amount'],
            scenario['years'],
            interest_rates_str,
            scenario['minimum_monthly_payment'],
            scenario['additional_payment'],
            scenario['refinance'],
            scenario['refinance_every_x_years'],
            scenario['refinance_when_principal_hit'],
            scenario['refinance_interest_will_increase'],
            f"✅ Loaded scenario '{scenario_name}'"
        )
        
    except Exception as e:
        return (
            4300000, 40, "2.3, 2.9, 3.5, 4.495, 4.495, 5.495",
            0, 0, False, 3, 3000000, 1.0,
            f"❌ Error loading scenario: {str(e)}"
        )

def compare_scenarios(selected_scenarios: List[str]) -> Tuple[gr.Plot, gr.Dataframe]:
    """Compare multiple scenarios and return comparison charts and table."""
    if len(selected_scenarios) < 2:
        empty_chart = go.Figure()
        empty_chart.add_annotation(
            text="Select at least 2 scenarios to compare",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False
        )
        empty_df = pd.DataFrame()
        return empty_chart, empty_df
    
    return comparison.generate_comparison(global_state.scenarios, selected_scenarios)

# Create Gradio Interface
def create_interface():
    """Create the main Gradio interface."""
    
    with gr.Blocks(
        theme=gr.themes.Soft(),
        css_paths=["assets/custom.css"],
        title="🏠 Mortgage Calculator"
    ) as interface:
        
        gr.Markdown("# 🏠 Mortgage Calculator")
        gr.Markdown("Calculate mortgage payments, compare scenarios, and analyze loan options.")
        
        with gr.Tabs():
            # Main Calculator Tab
            with gr.Tab("🧮 Calculator"):
                with gr.Row():
                    # Input Column
                    with gr.Column(scale=1):
                        gr.Markdown("## 📝 Loan Parameters")
                        
                        with gr.Group():
                            gr.Markdown("### 💰 Loan Details")
                            loan_amount = gr.Number(
                                label="Loan Amount ($)",
                                value=4300000,
                                minimum=10000,
                                maximum=10000000,
                                step=10000,
                            )
                            years = gr.Slider(
                                label="Loan Term (Years)",
                                minimum=5,
                                maximum=50,
                                value=40,
                                step=1,
                            )
                        
                        with gr.Group():
                            gr.Markdown("### 📈 Interest Rates")
                            interest_rates_str = gr.Textbox(
                                label="Interest Rates (%) - comma separated",
                                value="2.3, 2.9, 3.5, 4.495, 4.495, 5.495",
                                placeholder="e.g., 2.5, 3.0, 3.5",
                            )
                        
                        with gr.Group():
                            gr.Markdown("### 💳 Payment Settings")
                            minimum_monthly_payment = gr.Number(
                                label="Minimum Monthly Payment ($)",
                                value=0,
                                minimum=0,
                                step=100,
                            )
                            additional_payment = gr.Number(
                                label="Additional Monthly Payment ($)",
                                value=0,
                                minimum=0,
                                step=100,
                            )
                        
                        with gr.Group():
                            gr.Markdown("### 🔄 Refinancing Options")
                            refinance = gr.Checkbox(
                                label="Enable Refinancing",
                                value=False,
                            )
                            
                            with gr.Row():
                                refinance_every_x_years = gr.Number(
                                    label="Refinance Every (Years)",
                                    value=3,
                                    minimum=1,
                                    maximum=10,
                                    visible=False,
                                )
                                refinance_when_principal_hit = gr.Number(
                                    label="Principal Threshold ($)",
                                    value=3000000,
                                    minimum=100000,
                                    step=100000,
                                    visible=False,
                                )
                                refinance_interest_will_increase = gr.Number(
                                    label="Rate Increase (%)",
                                    value=1.0,
                                    minimum=0.0,
                                    maximum=5.0,
                                    step=0.1,
                                    visible=False,
                                )
                        
                        # Show/hide refinancing options
                        def toggle_refinance_options(refinance_enabled):
                            return {
                                refinance_every_x_years: gr.update(visible=refinance_enabled),
                                refinance_when_principal_hit: gr.update(visible=refinance_enabled),
                                refinance_interest_will_increase: gr.update(visible=refinance_enabled),
                            }
                        
                        refinance.change(
                            toggle_refinance_options,
                            inputs=[refinance],
                            outputs=[refinance_every_x_years, refinance_when_principal_hit, refinance_interest_will_increase]
                        )
                        
                        calculate_btn = gr.Button("🧮 Calculate", variant="primary", size="lg")
                    
                    # Results Column
                    with gr.Column(scale=2):
                        gr.Markdown("## 📊 Results")
                        
                        # Key Metrics
                        with gr.Row():
                            payoff_time = gr.Textbox(label="⏰ Payoff Time", interactive=False)
                            total_interest = gr.Textbox(label="💰 Total Interest", interactive=False)
                            total_paid = gr.Textbox(label="💸 Total Paid", interactive=False)
                            avg_monthly = gr.Textbox(label="📅 Avg Monthly", interactive=False)
                        
                        # Charts
                        with gr.Row():
                            payment_chart = gr.Plot(label="Payment Timeline")
                            balance_chart = gr.Plot(label="Loan Balance")
                        
                        # Amortization Table
                        amortization_table = gr.Dataframe(
                            label="📋 Amortization Schedule",
                            interactive=False,
                            wrap=True,
                        )
                
                # Wire up the calculation
                calculate_btn.click(
                    mortgage_calculator,
                    inputs=[
                        loan_amount, years, interest_rates_str,
                        minimum_monthly_payment, additional_payment,
                        refinance, refinance_every_x_years,
                        refinance_when_principal_hit, refinance_interest_will_increase
                    ],
                    outputs=[
                        payoff_time, total_interest, total_paid, avg_monthly,
                        payment_chart, balance_chart, amortization_table
                    ]
                )
                
                # Auto-calculate on input change
                for input_component in [
                    loan_amount, years, interest_rates_str,
                    minimum_monthly_payment, additional_payment,
                    refinance, refinance_every_x_years,
                    refinance_when_principal_hit, refinance_interest_will_increase
                ]:
                    input_component.change(
                        mortgage_calculator,
                        inputs=[
                            loan_amount, years, interest_rates_str,
                            minimum_monthly_payment, additional_payment,
                            refinance, refinance_every_x_years,
                            refinance_when_principal_hit, refinance_interest_will_increase
                        ],
                        outputs=[
                            payoff_time, total_interest, total_paid, avg_monthly,
                            payment_chart, balance_chart, amortization_table
                        ]
                    )
            
            # Scenario Management Tab
            with gr.Tab("💾 Scenarios"):
                gr.Markdown("## 💾 Scenario Management")
                gr.Markdown("Save and load different mortgage scenarios for comparison.")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Save Current Scenario")
                        scenario_name_input = gr.Textbox(
                            label="Scenario Name",
                            placeholder="e.g., Conservative Plan"
                        )
                        save_btn = gr.Button("💾 Save Scenario", variant="primary")
                        save_status = gr.Textbox(label="Status", interactive=False)
                    
                    with gr.Column():
                        gr.Markdown("### Load Saved Scenario")
                        scenario_dropdown = gr.Dropdown(
                            label="Select Scenario",
                            choices=[],
                            interactive=True
                        )
                        load_btn = gr.Button("📂 Load Scenario")
                        load_status = gr.Textbox(label="Status", interactive=False)
                
                # Update dropdown choices when interface loads
                def update_scenario_choices():
                    return gr.update(choices=list(global_state.scenarios.keys()))
                
                interface.load(update_scenario_choices, outputs=[scenario_dropdown])
                
                # Save scenario
                save_btn.click(
                    save_scenario,
                    inputs=[
                        scenario_name_input, loan_amount, years, interest_rates_str,
                        minimum_monthly_payment, additional_payment,
                        refinance, refinance_every_x_years,
                        refinance_when_principal_hit, refinance_interest_will_increase
                    ],
                    outputs=[save_status]
                ).then(
                    update_scenario_choices,
                    outputs=[scenario_dropdown]
                )
                
                # Load scenario
                load_btn.click(
                    load_scenario,
                    inputs=[scenario_dropdown],
                    outputs=[
                        loan_amount, years, interest_rates_str,
                        minimum_monthly_payment, additional_payment,
                        refinance, refinance_every_x_years,
                        refinance_when_principal_hit, refinance_interest_will_increase,
                        load_status
                    ]
                )
            
            # Comparison Tab
            with gr.Tab("🔍 Comparison"):
                gr.Markdown("## 🔍 Scenario Comparison")
                gr.Markdown("Compare multiple saved scenarios side-by-side.")
                
                with gr.Row():
                    scenarios_checklist = gr.CheckboxGroup(
                        label="Select Scenarios to Compare",
                        choices=[],
                        value=[]
                    )
                
                compare_btn = gr.Button("🔍 Compare Scenarios", variant="primary")
                
                with gr.Row():
                    comparison_chart = gr.Plot(label="Scenario Comparison")
                
                comparison_table = gr.Dataframe(
                    label="📊 Comparison Summary",
                    interactive=False
                )
                
                # Update comparison choices
                def update_comparison_choices():
                    choices = list(global_state.scenarios.keys())
                    return gr.update(choices=choices)
                
                interface.load(update_comparison_choices, outputs=[scenarios_checklist])
                
                # Perform comparison
                compare_btn.click(
                    compare_scenarios,
                    inputs=[scenarios_checklist],
                    outputs=[comparison_chart, comparison_table]
                )
    
    return interface

if __name__ == "__main__":
    # Create and launch the interface
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Set to True for public sharing
        debug=True,
    )
```

### 2. Chart Components (components/charts.py)
```python
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List

def create_payment_timeline_chart(calculation_result: Dict) -> go.Figure:
    """Create payment timeline chart showing principal vs interest."""
    months = list(range(1, len(calculation_result['principal']) + 1))
    
    fig = go.Figure()
    
    # Interest payments (bottom layer)
    fig.add_trace(go.Scatter(
        x=months,
        y=calculation_result['interest'],
        mode='lines',
        name='Interest',
        fill='tozeroy',
        fillcolor='rgba(239, 68, 68, 0.6)',
        line=dict(color='rgb(239, 68, 68)', width=2),
        hovertemplate='Month: %{x}<br>Interest: $%{y:,.0f}<extra></extra>'
    ))
    
    # Principal payments (top layer)
    fig.add_trace(go.Scatter(
        x=months,
        y=[p + i for p, i in zip(calculation_result['principal'], calculation_result['interest'])],
        mode='lines',
        name='Principal',
        fill='tonexty',
        fillcolor='rgba(16, 185, 129, 0.6)',
        line=dict(color='rgb(16, 185, 129)', width=2),
        hovertemplate='Month: %{x}<br>Total Payment: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Monthly Payment Breakdown Over Time",
        xaxis_title="Month",
        yaxis_title="Payment Amount ($)",
        hovermode='x unified',
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )
    
    return fig

def create_loan_balance_chart(calculation_result: Dict) -> go.Figure:
    """Create loan balance over time chart."""
    months = list(range(1, len(calculation_result['loan_end']) + 1))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=calculation_result['loan_end'],
        mode='lines',
        name='Remaining Balance',
        line=dict(color='rgb(30, 58, 138)', width=3),
        fill='tozeroy',
        fillcolor='rgba(30, 58, 138, 0.1)',
        hovertemplate='Month: %{x}<br>Balance: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Loan Balance Over Time",
        xaxis_title="Month",
        yaxis_title="Remaining Balance ($)",
        template='plotly_white',
        height=400
    )
    
    return fig

def create_interest_rate_timeline(calculation_result: Dict) -> go.Figure:
    """Create interest rate timeline chart."""
    months = list(range(1, len(calculation_result['interest_rate_yearly']) + 1))
    rates_percent = [rate * 100 for rate in calculation_result['interest_rate_yearly']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=rates_percent,
        mode='lines+markers',
        name='Interest Rate',
        line=dict(color='rgb(245, 158, 11)', width=2),
        marker=dict(size=4),
        hovertemplate='Month: %{x}<br>Rate: %{y:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Interest Rate Over Time",
        xaxis_title="Month",
        yaxis_title="Interest Rate (%)",
        template='plotly_white',
        height=300
    )
    
    return fig
```

### 3. Output Components (components/outputs.py)
```python
import pandas as pd
from typing import Dict
from utils.formatters import format_currency

def create_amortization_dataframe(calculation_result: Dict) -> pd.DataFrame:
    """Create formatted amortization schedule DataFrame."""
    df = pd.DataFrame(calculation_result)
    
    # Add month and year columns
    df['Month'] = range(1, len(df) + 1)
    df['Year'] = ((df['Month'] - 1) // 12) + 1
    df['Month_in_Year'] = ((df['Month'] - 1) % 12) + 1
    
    # Format currency columns
    currency_columns = ['loan_start', 'total', 'principal', 'interest', 'loan_end']
    for col in currency_columns:
        df[f'{col}_formatted'] = df[col].apply(format_currency)
    
    # Select and rename columns for display
    display_df = df[[
        'Month', 'Year', 'Month_in_Year',
        'total_formatted', 'principal_formatted', 
        'interest_formatted', 'loan_end_formatted'
    ]].copy()
    
    display_df.columns = [
        'Month', 'Year', 'Month in Year',
        'Total Payment', 'Principal', 
        'Interest', 'Remaining Balance'
    ]
    
    return display_df

def calculate_summary_metrics(calculation_result: Dict) -> Dict[str, str]:
    """Calculate and format summary metrics."""
    total_interest = sum(calculation_result['interest'])
    total_paid = sum(calculation_result['total'])
    months_count = len(calculation_result['total'])
    years_taken = months_count // 12
    months_remaining = months_count % 12
    avg_monthly = total_paid / months_count if months_count > 0 else 0
    
    return {
        'payoff_time': f"{years_taken}Y {months_remaining}M",
        'total_interest': format_currency(total_interest),
        'total_paid': format_currency(total_paid),
        'avg_monthly': format_currency(avg_monthly),
    }
```

### 4. Comparison Components (components/comparison.py)
```python
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Tuple
from logic import calculate_monthly_payment
from utils.formatters import format_currency

def generate_comparison(scenarios: Dict, selected_scenarios: List[str]) -> Tuple[go.Figure, pd.DataFrame]:
    """Generate comparison chart and table for selected scenarios."""
    
    if len(selected_scenarios) < 2:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Select at least 2 scenarios to compare",
            x=0.5, y=0.5, xref="paper", yref="paper",
            showarrow=False, font=dict(size=16)
        )
        return empty_fig, pd.DataFrame()
    
    # Calculate results for each scenario
    scenario_results = {}
    comparison_data = []
    
    colors = ['#1e3a8a', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
    
    fig = go.Figure()
    
    for i, scenario_name in enumerate(selected_scenarios):
        if scenario_name not in scenarios:
            continue
            
        scenario = scenarios[scenario_name]
        
        # Calculate mortgage for this scenario
        result = calculate_monthly_payment(**scenario)
        scenario_results[scenario_name] = result
        
        # Add to comparison chart
        months = list(range(1, len(result['loan_end']) + 1))
        fig.add_trace(go.Scatter(
            x=months,
            y=result['loan_end'],
            mode='lines',
            name=scenario_name,
            line=dict(color=colors[i % len(colors)], width=3),
            hovertemplate=f'{scenario_name}<br>Month: %{{x}}<br>Balance: $%{{y:,.0f}}<extra></extra>'
        ))
        
        # Calculate summary metrics for table
        total_interest = sum(result['interest'])
        total_paid = sum(result['total'])
        months_count = len(result['total'])
        years_taken = months_count // 12
        months_remaining = months_count % 12
        avg_monthly = total_paid / months_count if months_count > 0 else 0
        
        comparison_data.append({
            'Scenario': scenario_name,
            'Loan Amount': format_currency(scenario['loan_amount']),
            'Term (Years)': scenario['years'],
            'Avg Interest Rate': f"{sum(scenario['interest_rates'])/len(scenario['interest_rates']):.2f}%",
            'Payoff Time': f"{years_taken}Y {months_remaining}M",
            'Total Interest': format_currency(total_interest),
            'Total Paid': format_currency(total_paid),
            'Avg Monthly': format_currency(avg_monthly),
            'Additional Payment': format_currency(scenario['additional_payment']),
        })
    
    fig.update_layout(
        title="Loan Balance Comparison",
        xaxis_title="Month",
        yaxis_title="Remaining Balance ($)",
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500
    )
    
    # Create comparison DataFrame
    comparison_df = pd.DataFrame(comparison_data)
    
    return fig, comparison_df

def create_payment_comparison_chart(scenarios: Dict, selected_scenarios: List[str]) -> go.Figure:
    """Create payment comparison chart showing monthly payments over time."""
    fig = go.Figure()
    colors = ['#1e3a8a', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
    
    for i, scenario_name in enumerate(selected_scenarios):
        if scenario_name not in scenarios:
            continue
            
        scenario = scenarios[scenario_name]
        result = calculate_monthly_payment(**scenario)
        
        months = list(range(1, len(result['total']) + 1))
        fig.add_trace(go.Scatter(
            x=months,
            y=result['total'],
            mode='lines',
            name=scenario_name,
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate=f'{scenario_name}<br>Month: %{{x}}<br>Payment: $%{{y:,.0f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title="Monthly Payment Comparison",
        xaxis_title="Month",
        yaxis_title="Monthly Payment ($)",
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )
    
    return fig
```

### 5. Utilities (utils/state.py)
```python
from typing import Dict, Any

class GlobalState:
    """Simple global state management for Gradio app."""
    
    def __init__(self):
        self.scenarios: Dict[str, Dict[str, Any]] = {}
    
    def save_scenario(self, name: str, parameters: Dict[str, Any]):
        """Save a scenario with the given name and parameters."""
        self.scenarios[name] = parameters.copy()
    
    def load_scenario(self, name: str) -> Dict[str, Any]:
        """Load a scenario by name."""
        return self.scenarios.get(name, {})
    
    def delete_scenario(self, name: str):
        """Delete a scenario by name."""
        if name in self.scenarios:
            del self.scenarios[name]
    
    def list_scenarios(self) -> list:
        """Get list of all scenario names."""
        return list(self.scenarios.keys())
```

### 6. Utilities (utils/formatters.py)
```python
def format_currency(amount: float) -> str:
    """Format a number as currency."""
    return f"${amount:,.0f}"

def format_percentage(rate: float) -> str:
    """Format a decimal as percentage."""
    return f"{rate:.2f}%"

def parse_interest_rates(rates_str: str) -> list:
    """Parse comma-separated interest rates string."""
    try:
        return [float(x.strip()) for x in rates_str.split(',') if x.strip()]
    except ValueError:
        raise ValueError("Invalid interest rate format. Use comma-separated numbers.")
```

### 7. Custom Styling (assets/custom.css)
```css
/* Custom Gradio styling */
.gradio-container {
    font-family: 'Inter', sans-serif !important;
    max-width: 1400px !important;
}

/* Header styling */
.gradio-container h1 {
    color: #1e3a8a;
    text-align: center;
    margin-bottom: 1rem;
}

/* Button styling */
.gradio-container .primary {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.gradio-container .primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3) !important;
}

/* Input styling */
.gradio-container input, .gradio-container textarea {
    border-radius: 6px !important;
    border: 2px solid #e5e7eb !important;
    transition: border-color 0.2s ease !important;
}

.gradio-container input:focus, .gradio-container textarea:focus {
    border-color: #1e3a8a !important;
    box-shadow: 0 0 0 3px rgba(30, 58, 138, 0.1) !important;
}

/* Card styling */
.gradio-container .block {
    border-radius: 12px !important;
    border: 1px solid #e5e7eb !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
}

/* Tab styling */
.gradio-container .tab-nav button {
    border-radius: 8px 8px 0 0 !important;
    font-weight: 500 !important;
}

.gradio-container .tab-nav button.selected {
    background-color: #1e3a8a !important;
    color: white !important;
}

/* Metric cards */
.gradio-container .output-textbox {
    background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%) !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    text-align: center !important;
}

/* Chart containers */
.gradio-container .plot-container {
    border-radius: 12px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}
```

## Deployment

### Local Development
```bash
# Install dependencies
pip install gradio pandas plotly numpy matplotlib

# Run the application
python app.py
```

### Gradio Sharing
```python
# In app.py, set share=True for public link
interface.launch(share=True)
```

### HuggingFace Spaces Deployment
```python
# Create app.py in HuggingFace Space
# Add requirements.txt with dependencies
# Space will auto-deploy on git push
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
```

### Requirements.txt
```
gradio>=4.0.0
pandas>=1.5.0
plotly>=5.0.0
numpy>=1.24.0
matplotlib>=3.7.0
```

This Gradio-specific plan provides a complete implementation using Gradio's simple yet powerful interface generation capabilities, with automatic UI creation, real-time updates, and easy deployment options.