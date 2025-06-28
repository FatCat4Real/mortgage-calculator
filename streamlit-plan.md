# Streamlit Mortgage Calculator - Implementation Plan

Based on the core-plan.md, this document provides specific Streamlit implementation details.

## Streamlit-Specific Implementation

### Framework Setup
- **Framework**: Streamlit 1.28+
- **Dependencies**:
  ```
  streamlit>=1.28.0
  pandas>=1.5.0
  plotly>=5.0.0
  numpy>=1.24.0
  ```
- **Additional Packages**:
  - `streamlit-option-menu` for enhanced navigation
  - `streamlit-aggrid` for advanced data tables
  - `streamlit-plotly-events` for chart interactions

### Project Structure
```
mortgage_calculator_streamlit/
├── app.py                    # Main Streamlit application
├── logic.py                  # Existing calculation logic (unchanged)
├── components/
│   ├── __init__.py
│   ├── inputs.py            # Streamlit input widgets
│   ├── outputs.py           # Results display components
│   ├── charts.py            # Plotly chart components
│   └── comparison.py        # Multi-scenario comparison
├── styles/
│   └── style.css           # Custom CSS styling
├── utils/
│   ├── __init__.py
│   ├── helpers.py          # Utility functions
│   └── formatters.py       # Number/currency formatting
└── config/
    └── settings.py         # App configuration
```

## Streamlit Implementation Details

### 1. App Structure (app.py)
```python
import streamlit as st
from components import inputs, outputs, charts, comparison
from utils import helpers

# Page config
st.set_page_config(
    page_title="Mortgage Calculator",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('styles/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Main app logic
def main():
    # Initialize session state
    helpers.init_session_state()
    
    # Sidebar inputs
    inputs.render_sidebar()
    
    # Main dashboard
    outputs.render_dashboard()
    
    # Comparison section (if enabled)
    if st.session_state.get('comparison_mode', False):
        comparison.render_comparison()

if __name__ == "__main__":
    main()
```

### 2. Input Components (components/inputs.py)

#### Core Parameters
```python
def render_loan_inputs():
    st.subheader("💰 Loan Details")
    
    col1, col2 = st.columns(2)
    with col1:
        loan_amount = st.number_input(
            "Loan Amount ($)",
            min_value=10000,
            max_value=10000000,
            value=4300000,
            step=10000,
            format="%d"
        )
    
    with col2:
        loan_years = st.slider(
            "Loan Term (Years)",
            min_value=5,
            max_value=50,
            value=40,
            step=1
        )
    
    return loan_amount, loan_years

def render_interest_rates():
    st.subheader("📈 Interest Rates")
    
    # Dynamic interest rate input
    if 'interest_rates' not in st.session_state:
        st.session_state.interest_rates = [2.3, 2.9, 3.5, 4.495, 4.495, 5.495]
    
    # Add/remove rate functionality
    col1, col2 = st.columns([3, 1])
    with col1:
        new_rate = st.number_input("Add Rate (%)", min_value=0.1, max_value=20.0, step=0.1)
    with col2:
        if st.button("➕ Add"):
            st.session_state.interest_rates.append(new_rate)
    
    # Display current rates with remove option
    for i, rate in enumerate(st.session_state.interest_rates):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.session_state.interest_rates[i] = st.number_input(
                f"Year {i+1} Rate (%)",
                value=rate,
                min_value=0.1,
                max_value=20.0,
                step=0.1,
                key=f"rate_{i}"
            )
        with col2:
            if st.button("🗑️", key=f"remove_{i}"):
                st.session_state.interest_rates.pop(i)
                st.experimental_rerun()
```

#### Payment Settings
```python
def render_payment_inputs():
    st.subheader("💳 Payment Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        min_payment = st.number_input(
            "Minimum Monthly Payment ($)",
            min_value=0,
            value=0,
            step=100
        )
    
    with col2:
        additional_payment = st.number_input(
            "Additional Monthly Payment ($)",
            min_value=0,
            value=0,
            step=100
        )
    
    return min_payment, additional_payment
```

#### Refinancing Options
```python
def render_refinancing_inputs():
    st.subheader("🔄 Refinancing Options")
    
    refinance = st.checkbox("Enable Refinancing", value=False)
    
    if refinance:
        col1, col2, col3 = st.columns(3)
        with col1:
            refinance_cycle = st.number_input(
                "Refinance Every (Years)",
                min_value=1,
                max_value=10,
                value=3
            )
        
        with col2:
            refinance_threshold = st.number_input(
                "Principal Threshold ($)",
                min_value=100000,
                value=3000000,
                step=100000
            )
        
        with col3:
            rate_increase = st.number_input(
                "Rate Increase (%)",
                min_value=0.0,
                max_value=5.0,
                value=1.0,
                step=0.1
            )
        
        return refinance, refinance_cycle, refinance_threshold, rate_increase
    
    return refinance, 3, 3000000, 1.0
```

### 3. Output Components (components/outputs.py)

#### Key Metrics Cards
```python
def render_metrics_cards(calculation_result):
    st.subheader("📊 Key Metrics")
    
    # Calculate summary metrics
    total_interest = sum(calculation_result['interest'])
    total_paid = sum(calculation_result['total'])
    months_count = len(calculation_result['total'])
    years = months_count // 12
    months = months_count % 12
    avg_monthly = total_paid / months_count if months_count > 0 else 0
    
    # Display in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Payoff Time",
            f"{years}Y {months}M",
            delta=None
        )
    
    with col2:
        st.metric(
            "Total Interest",
            f"${total_interest:,.0f}",
            delta=None
        )
    
    with col3:
        st.metric(
            "Total Paid",
            f"${total_paid:,.0f}",
            delta=None
        )
    
    with col4:
        st.metric(
            "Avg Monthly",
            f"${avg_monthly:,.0f}",
            delta=None
        )
```

#### Amortization Schedule
```python
def render_amortization_table(calculation_result):
    st.subheader("📋 Amortization Schedule")
    
    # Convert to DataFrame
    df = pd.DataFrame(calculation_result)
    
    # Add calculated columns
    df['Month'] = range(1, len(df) + 1)
    df['Year'] = (df['Month'] - 1) // 12 + 1
    df['Month_in_Year'] = ((df['Month'] - 1) % 12) + 1
    
    # Format currency columns
    currency_cols = ['loan_start', 'total', 'principal', 'interest', 'loan_end']
    for col in currency_cols:
        df[col] = df[col].apply(lambda x: f"${x:,.0f}")
    
    # Display with AgGrid for better interaction
    from st_aggrid import AgGrid, GridOptionsBuilder
    
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
    
    grid_options = gb.build()
    
    AgGrid(
        df,
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        height=400
    )
```

### 4. Chart Components (components/charts.py)

#### Payment Timeline Chart
```python
def render_payment_timeline(calculation_result):
    import plotly.graph_objects as go
    
    df = pd.DataFrame(calculation_result)
    df['Month'] = range(1, len(df) + 1)
    
    fig = go.Figure()
    
    # Principal payments
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['principal'],
        mode='lines',
        name='Principal',
        fill='tonexty',
        fillcolor='rgba(16, 185, 129, 0.3)',
        line=dict(color='rgb(16, 185, 129)')
    ))
    
    # Interest payments
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['interest'],
        mode='lines',
        name='Interest',
        fill='tozeroy',
        fillcolor='rgba(239, 68, 68, 0.3)',
        line=dict(color='rgb(239, 68, 68)')
    ))
    
    fig.update_layout(
        title="Monthly Payment Breakdown",
        xaxis_title="Month",
        yaxis_title="Payment ($)",
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def render_loan_balance_chart(calculation_result):
    import plotly.graph_objects as go
    
    df = pd.DataFrame(calculation_result)
    df['Month'] = range(1, len(df) + 1)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['loan_end'],
        mode='lines',
        name='Remaining Balance',
        line=dict(color='rgb(30, 58, 138)', width=3)
    ))
    
    fig.update_layout(
        title="Loan Balance Over Time",
        xaxis_title="Month",
        yaxis_title="Remaining Balance ($)",
        template='plotly_white'
    )
    
    return fig
```

### 5. Comparison Components (components/comparison.py)

#### Multi-Scenario Manager
```python
def render_scenario_manager():
    st.subheader("🔍 Scenario Comparison")
    
    # Initialize scenarios in session state
    if 'scenarios' not in st.session_state:
        st.session_state.scenarios = {}
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        scenario_name = st.text_input("Scenario Name", placeholder="e.g., Conservative")
    
    with col2:
        if st.button("💾 Save Current"):
            if scenario_name:
                current_params = get_current_parameters()
                st.session_state.scenarios[scenario_name] = current_params
                st.success(f"Saved scenario: {scenario_name}")
    
    with col3:
        if st.session_state.scenarios:
            selected_scenario = st.selectbox("Load Scenario", list(st.session_state.scenarios.keys()))
            if st.button("📂 Load"):
                load_scenario(st.session_state.scenarios[selected_scenario])

def render_comparison_dashboard():
    if len(st.session_state.scenarios) < 2:
        st.info("Save at least 2 scenarios to enable comparison")
        return
    
    # Select scenarios to compare
    scenarios_to_compare = st.multiselect(
        "Select Scenarios to Compare",
        list(st.session_state.scenarios.keys()),
        max_selections=4
    )
    
    if len(scenarios_to_compare) >= 2:
        # Calculate results for each scenario
        comparison_results = {}
        for scenario_name in scenarios_to_compare:
            params = st.session_state.scenarios[scenario_name]
            result = calculate_monthly_payment(**params)
            comparison_results[scenario_name] = result
        
        # Render comparison charts and tables
        render_comparison_metrics(comparison_results)
        render_comparison_charts(comparison_results)
```

### 6. Styling (styles/style.css)

```css
/* Custom Streamlit styling */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Metric cards styling */
[data-testid="metric-container"] {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

/* Sidebar styling */
.css-1d391kg {
    background-color: #1e3a8a;
}

/* Button styling */
.stButton > button {
    background-color: #f59e0b;
    color: white;
    border: none;
    border-radius: 0.375rem;
    transition: all 0.2s;
}

.stButton > button:hover {
    background-color: #d97706;
    transform: translateY(-1px);
}

/* Input styling */
.stNumberInput > div > div > input {
    border-radius: 0.375rem;
    border: 1px solid #d1d5db;
}

/* Chart container */
.plotly-graph-div {
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}
```

### 7. Configuration (config/settings.py)

```python
# App configuration
APP_CONFIG = {
    'page_title': 'Mortgage Calculator',
    'page_icon': '🏠',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Default values
DEFAULT_VALUES = {
    'loan_amount': 4_300_000,
    'years': 40,
    'interest_rates': [2.3, 2.9, 3.5, 4.495, 4.495, 5.495],
    'minimum_monthly_payment': 0,
    'additional_payment': 0,
    'refinance': False,
    'refinance_every_x_years': 3,
    'refinance_when_principal_hit': 3_000_000,
    'refinance_interest_will_increase': 1.0
}

# Chart colors (matching design system)
COLORS = {
    'primary': '#1e3a8a',
    'secondary': '#10b981',
    'accent': '#f59e0b',
    'background': '#f9fafb',
    'text': '#374151',
    'error': '#ef4444'
}
```

## Deployment

### Local Development
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Streamlit Cloud Deployment
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Configure secrets if needed
4. Deploy automatically on push

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

This Streamlit-specific plan provides all the implementation details needed to build the mortgage calculator using Streamlit's components and patterns.