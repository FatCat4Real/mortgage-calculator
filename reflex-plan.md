# Reflex Mortgage Calculator - Implementation Plan

Based on the core-plan.md, this document provides specific Reflex implementation details.

## Reflex-Specific Implementation

### Framework Setup
- **Framework**: Reflex 0.4.0+
- **Dependencies**:
  ```
  reflex>=0.4.0
  pandas>=1.5.0
  plotly>=5.0.0
  numpy>=1.24.0
  ```
- **Additional Features**:
  - Native Python reactivity
  - Built-in state management
  - Component-based architecture
  - TypeScript-like type hints

### Project Structure
```
mortgage_calculator_reflex/
├── rxconfig.py                 # Reflex configuration
├── mortgage_calculator/
│   ├── __init__.py
│   ├── mortgage_calculator.py  # Main app
│   ├── logic.py               # Existing calculation logic
│   ├── state.py               # Reflex state management
│   ├── components/
│   │   ├── __init__.py
│   │   ├── inputs.py          # Input components
│   │   ├── outputs.py         # Results display components
│   │   ├── charts.py          # Chart components
│   │   └── comparison.py      # Multi-scenario comparison
│   ├── styles/
│   │   └── styles.py          # Reflex styling
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py         # Utility functions
│       └── formatters.py      # Number/currency formatting
└── assets/                    # Static assets
```

## Reflex Implementation Details

### 1. Configuration (rxconfig.py)
```python
import reflex as rx

class Config(rx.Config):
    app_name = "mortgage_calculator"
    db_url = "sqlite:///reflex.db"
    env = rx.Env.DEV

config = Config()
```

### 2. State Management (state.py)
```python
import reflex as rx
from typing import List, Dict, Any
from .logic import calculate_monthly_payment

class MortgageState(rx.State):
    # Core parameters
    loan_amount: int = 4_300_000
    years: int = 40
    interest_rates: List[float] = [2.3, 2.9, 3.5, 4.495, 4.495, 5.495]
    minimum_monthly_payment: int = 0
    additional_payment: int = 0
    
    # Refinancing parameters
    refinance: bool = False
    refinance_every_x_years: int = 3
    refinance_when_principal_hit: int = 3_000_000
    refinance_interest_will_increase: float = 1.0
    
    # Calculation results
    calculation_result: Dict[str, List] = {}
    
    # Comparison state
    scenarios: Dict[str, Dict] = {}
    selected_scenarios: List[str] = []
    comparison_mode: bool = False
    
    # UI state
    loading: bool = False
    error_message: str = ""
    
    @rx.var
    def total_interest(self) -> int:
        """Calculate total interest paid."""
        if not self.calculation_result.get('interest'):
            return 0
        return sum(self.calculation_result['interest'])
    
    @rx.var
    def total_paid(self) -> int:
        """Calculate total amount paid."""
        if not self.calculation_result.get('total'):
            return 0
        return sum(self.calculation_result['total'])
    
    @rx.var
    def payoff_time(self) -> str:
        """Calculate payoff time in years and months."""
        if not self.calculation_result.get('total'):
            return "0Y 0M"
        months = len(self.calculation_result['total'])
        years = months // 12
        remaining_months = months % 12
        return f"{years}Y {remaining_months}M"
    
    @rx.var
    def average_monthly(self) -> int:
        """Calculate average monthly payment."""
        if not self.calculation_result.get('total'):
            return 0
        total = sum(self.calculation_result['total'])
        months = len(self.calculation_result['total'])
        return int(total / months) if months > 0 else 0
    
    def calculate(self):
        """Perform mortgage calculation."""
        self.loading = True
        self.error_message = ""
        
        try:
            self.calculation_result = calculate_monthly_payment(
                loan=self.loan_amount,
                years=self.years,
                interest_rates_100=self.interest_rates,
                minimum_monthly_payment=self.minimum_monthly_payment,
                additional_payment=self.additional_payment,
                refinance=self.refinance,
                refinance_every_x_years=self.refinance_every_x_years,
                refinance_when_principal_hit=self.refinance_when_principal_hit,
                refinance_interest_will_increase=self.refinance_interest_will_increase,
            )
        except Exception as e:
            self.error_message = f"Calculation error: {str(e)}"
        finally:
            self.loading = False
    
    def add_interest_rate(self, rate: float):
        """Add new interest rate to the list."""
        self.interest_rates.append(rate)
        self.calculate()
    
    def remove_interest_rate(self, index: int):
        """Remove interest rate at given index."""
        if 0 <= index < len(self.interest_rates):
            self.interest_rates.pop(index)
            self.calculate()
    
    def update_interest_rate(self, index: int, rate: float):
        """Update interest rate at given index."""
        if 0 <= index < len(self.interest_rates):
            self.interest_rates[index] = rate
            self.calculate()
    
    def save_scenario(self, name: str):
        """Save current parameters as a scenario."""
        if name:
            self.scenarios[name] = {
                'loan_amount': self.loan_amount,
                'years': self.years,
                'interest_rates': self.interest_rates.copy(),
                'minimum_monthly_payment': self.minimum_monthly_payment,
                'additional_payment': self.additional_payment,
                'refinance': self.refinance,
                'refinance_every_x_years': self.refinance_every_x_years,
                'refinance_when_principal_hit': self.refinance_when_principal_hit,
                'refinance_interest_will_increase': self.refinance_interest_will_increase,
            }
    
    def load_scenario(self, name: str):
        """Load parameters from a saved scenario."""
        if name in self.scenarios:
            scenario = self.scenarios[name]
            self.loan_amount = scenario['loan_amount']
            self.years = scenario['years']
            self.interest_rates = scenario['interest_rates']
            self.minimum_monthly_payment = scenario['minimum_monthly_payment']
            self.additional_payment = scenario['additional_payment']
            self.refinance = scenario['refinance']
            self.refinance_every_x_years = scenario['refinance_every_x_years']
            self.refinance_when_principal_hit = scenario['refinance_when_principal_hit']
            self.refinance_interest_will_increase = scenario['refinance_interest_will_increase']
            self.calculate()
    
    def delete_scenario(self, name: str):
        """Delete a saved scenario."""
        if name in self.scenarios:
            del self.scenarios[name]
            if name in self.selected_scenarios:
                self.selected_scenarios.remove(name)
    
    def toggle_comparison_mode(self):
        """Toggle comparison mode on/off."""
        self.comparison_mode = not self.comparison_mode
```

### 3. Input Components (components/inputs.py)
```python
import reflex as rx
from ..state import MortgageState

def loan_inputs() -> rx.Component:
    """Render loan amount and term inputs."""
    return rx.vstack(
        rx.heading("💰 Loan Details", size="md"),
        rx.hstack(
            rx.vstack(
                rx.text("Loan Amount ($)"),
                rx.number_input(
                    value=MortgageState.loan_amount,
                    on_change=lambda x: MortgageState.set_loan_amount(int(x) if x else 0),
                    min_value=10000,
                    max_value=10000000,
                    step=10000,
                ),
                width="50%",
            ),
            rx.vstack(
                rx.text("Loan Term (Years)"),
                rx.slider(
                    value=MortgageState.years,
                    on_change=MortgageState.set_years,
                    min_value=5,
                    max_value=50,
                    step=1,
                ),
                rx.text(MortgageState.years),
                width="50%",
            ),
            width="100%",
        ),
        spacing="4",
        width="100%",
    )

def interest_rate_inputs() -> rx.Component:
    """Render interest rate inputs with dynamic add/remove."""
    return rx.vstack(
        rx.heading("📈 Interest Rates", size="md"),
        rx.hstack(
            rx.number_input(
                placeholder="New rate (%)",
                on_blur=lambda x: MortgageState.add_interest_rate(float(x) if x else 0),
                min_value=0.1,
                max_value=20.0,
                step=0.1,
            ),
            rx.button("➕ Add", on_click=lambda: None),
            spacing="2",
        ),
        rx.foreach(
            MortgageState.interest_rates,
            lambda rate, index: rx.hstack(
                rx.number_input(
                    value=rate,
                    on_change=lambda x: MortgageState.update_interest_rate(index, float(x) if x else 0),
                    min_value=0.1,
                    max_value=20.0,
                    step=0.1,
                ),
                rx.button(
                    "🗑️",
                    on_click=lambda: MortgageState.remove_interest_rate(index),
                    color_scheme="red",
                    size="sm",
                ),
                spacing="2",
                align="center",
            ),
        ),
        spacing="2",
        width="100%",
    )

def payment_inputs() -> rx.Component:
    """Render payment settings inputs."""
    return rx.vstack(
        rx.heading("💳 Payment Settings", size="md"),
        rx.hstack(
            rx.vstack(
                rx.text("Minimum Monthly Payment ($)"),
                rx.number_input(
                    value=MortgageState.minimum_monthly_payment,
                    on_change=lambda x: MortgageState.set_minimum_monthly_payment(int(x) if x else 0),
                    min_value=0,
                    step=100,
                ),
                width="50%",
            ),
            rx.vstack(
                rx.text("Additional Monthly Payment ($)"),
                rx.number_input(
                    value=MortgageState.additional_payment,
                    on_change=lambda x: MortgageState.set_additional_payment(int(x) if x else 0),
                    min_value=0,
                    step=100,
                ),
                width="50%",
            ),
            width="100%",
        ),
        spacing="4",
        width="100%",
    )

def refinancing_inputs() -> rx.Component:
    """Render refinancing options."""
    return rx.vstack(
        rx.heading("🔄 Refinancing Options", size="md"),
        rx.checkbox(
            "Enable Refinancing",
            is_checked=MortgageState.refinance,
            on_change=MortgageState.set_refinance,
        ),
        rx.cond(
            MortgageState.refinance,
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Refinance Every (Years)"),
                        rx.number_input(
                            value=MortgageState.refinance_every_x_years,
                            on_change=lambda x: MortgageState.set_refinance_every_x_years(int(x) if x else 3),
                            min_value=1,
                            max_value=10,
                        ),
                        width="33%",
                    ),
                    rx.vstack(
                        rx.text("Principal Threshold ($)"),
                        rx.number_input(
                            value=MortgageState.refinance_when_principal_hit,
                            on_change=lambda x: MortgageState.set_refinance_when_principal_hit(int(x) if x else 3000000),
                            min_value=100000,
                            step=100000,
                        ),
                        width="33%",
                    ),
                    rx.vstack(
                        rx.text("Rate Increase (%)"),
                        rx.number_input(
                            value=MortgageState.refinance_interest_will_increase,
                            on_change=lambda x: MortgageState.set_refinance_interest_will_increase(float(x) if x else 1.0),
                            min_value=0.0,
                            max_value=5.0,
                            step=0.1,
                        ),
                        width="33%",
                    ),
                    width="100%",
                ),
                spacing="4",
            ),
        ),
        spacing="4",
        width="100%",
    )

def sidebar() -> rx.Component:
    """Complete sidebar with all inputs."""
    return rx.vstack(
        loan_inputs(),
        interest_rate_inputs(),
        payment_inputs(),
        refinancing_inputs(),
        rx.button(
            "Calculate",
            on_click=MortgageState.calculate,
            loading=MortgageState.loading,
            width="100%",
            size="lg",
            color_scheme="blue",
        ),
        spacing="6",
        padding="4",
        width="350px",
        height="100vh",
        overflow_y="auto",
        border_right="1px solid #e2e8f0",
    )
```

### 4. Output Components (components/outputs.py)
```python
import reflex as rx
from ..state import MortgageState

def metric_card(title: str, value: str, icon: str = "") -> rx.Component:
    """Individual metric card component."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(icon, font_size="2xl"),
                rx.text(title, font_weight="medium", color="gray.600"),
                spacing="2",
                align="center",
            ),
            rx.text(value, font_size="2xl", font_weight="bold", color="gray.900"),
            spacing="2",
            align="start",
        ),
        padding="4",
        border="1px solid #e2e8f0",
        border_radius="lg",
        bg="white",
        shadow="sm",
    )

def metrics_dashboard() -> rx.Component:
    """Key metrics dashboard."""
    return rx.vstack(
        rx.heading("📊 Key Metrics", size="lg"),
        rx.grid(
            metric_card("Payoff Time", MortgageState.payoff_time, "⏰"),
            metric_card("Total Interest", f"${MortgageState.total_interest:,}", "💰"),
            metric_card("Total Paid", f"${MortgageState.total_paid:,}", "💸"),
            metric_card("Avg Monthly", f"${MortgageState.average_monthly:,}", "📅"),
            columns=4,
            spacing="4",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )

def amortization_table() -> rx.Component:
    """Amortization schedule table."""
    return rx.vstack(
        rx.heading("📋 Amortization Schedule", size="lg"),
        rx.cond(
            MortgageState.calculation_result,
            rx.table(
                headers=["Month", "Payment", "Principal", "Interest", "Balance"],
                rows=rx.foreach(
                    enumerate(MortgageState.calculation_result.get("total", [])),
                    lambda item: [
                        str(item[0] + 1),
                        f"${item[1]:,}",
                        f"${MortgageState.calculation_result['principal'][item[0]]:,}",
                        f"${MortgageState.calculation_result['interest'][item[0]]:,}",
                        f"${MortgageState.calculation_result['loan_end'][item[0]]:,}",
                    ],
                ),
                variant="striped",
                size="sm",
            ),
            rx.text("No calculation results available"),
        ),
        spacing="4",
        width="100%",
    )

def error_display() -> rx.Component:
    """Error message display."""
    return rx.cond(
        MortgageState.error_message != "",
        rx.alert(
            rx.alert_icon(),
            rx.alert_title("Calculation Error"),
            rx.alert_description(MortgageState.error_message),
            status="error",
        ),
    )
```

### 5. Chart Components (components/charts.py)
```python
import reflex as rx
from ..state import MortgageState

def payment_timeline_chart() -> rx.Component:
    """Payment timeline chart showing principal vs interest."""
    return rx.vstack(
        rx.heading("Payment Timeline", size="md"),
        rx.cond(
            MortgageState.calculation_result,
            rx.plotly(
                data=[
                    {
                        "x": list(range(1, len(MortgageState.calculation_result.get("principal", [])) + 1)),
                        "y": MortgageState.calculation_result.get("principal", []),
                        "type": "scatter",
                        "mode": "lines",
                        "fill": "tonexty",
                        "name": "Principal",
                        "line": {"color": "#10b981"},
                    },
                    {
                        "x": list(range(1, len(MortgageState.calculation_result.get("interest", [])) + 1)),
                        "y": MortgageState.calculation_result.get("interest", []),
                        "type": "scatter",
                        "mode": "lines",
                        "fill": "tozeroy",
                        "name": "Interest",
                        "line": {"color": "#ef4444"},
                    },
                ],
                layout={
                    "title": "Monthly Payment Breakdown",
                    "xaxis": {"title": "Month"},
                    "yaxis": {"title": "Payment ($)"},
                    "hovermode": "x unified",
                    "template": "plotly_white",
                },
            ),
            rx.text("No data to display"),
        ),
        spacing="4",
        width="100%",
    )

def loan_balance_chart() -> rx.Component:
    """Loan balance over time chart."""
    return rx.vstack(
        rx.heading("Loan Balance", size="md"),
        rx.cond(
            MortgageState.calculation_result,
            rx.plotly(
                data=[
                    {
                        "x": list(range(1, len(MortgageState.calculation_result.get("loan_end", [])) + 1)),
                        "y": MortgageState.calculation_result.get("loan_end", []),
                        "type": "scatter",
                        "mode": "lines",
                        "name": "Remaining Balance",
                        "line": {"color": "#1e3a8a", "width": 3},
                    }
                ],
                layout={
                    "title": "Loan Balance Over Time",
                    "xaxis": {"title": "Month"},
                    "yaxis": {"title": "Remaining Balance ($)"},
                    "template": "plotly_white",
                },
            ),
            rx.text("No data to display"),
        ),
        spacing="4",
        width="100%",
    )

def charts_section() -> rx.Component:
    """Charts section with tabs."""
    return rx.vstack(
        rx.heading("📈 Visualizations", size="lg"),
        rx.tabs(
            rx.tab_list(
                rx.tab("Payment Timeline"),
                rx.tab("Loan Balance"),
            ),
            rx.tab_panels(
                rx.tab_panel(payment_timeline_chart()),
                rx.tab_panel(loan_balance_chart()),
            ),
        ),
        spacing="4",
        width="100%",
    )
```

### 6. Comparison Components (components/comparison.py)
```python
import reflex as rx
from ..state import MortgageState

def scenario_manager() -> rx.Component:
    """Scenario management interface."""
    return rx.vstack(
        rx.heading("🔍 Scenario Management", size="lg"),
        rx.hstack(
            rx.input(
                placeholder="Scenario name",
                id="scenario_name",
            ),
            rx.button(
                "💾 Save Current",
                on_click=lambda: MortgageState.save_scenario(rx.get_value("scenario_name")),
            ),
            spacing="2",
        ),
        rx.cond(
            len(MortgageState.scenarios) > 0,
            rx.vstack(
                rx.text("Saved Scenarios:", font_weight="medium"),
                rx.foreach(
                    MortgageState.scenarios,
                    lambda name: rx.hstack(
                        rx.text(name),
                        rx.button(
                            "📂 Load",
                            on_click=lambda: MortgageState.load_scenario(name),
                            size="sm",
                        ),
                        rx.button(
                            "🗑️ Delete",
                            on_click=lambda: MortgageState.delete_scenario(name),
                            color_scheme="red",
                            size="sm",
                        ),
                        spacing="2",
                        align="center",
                    ),
                ),
                spacing="2",
            ),
        ),
        rx.button(
            "🔄 Toggle Comparison Mode",
            on_click=MortgageState.toggle_comparison_mode,
            color_scheme="purple",
        ),
        spacing="4",
        width="100%",
    )

def comparison_dashboard() -> rx.Component:
    """Multi-scenario comparison dashboard."""
    return rx.cond(
        MortgageState.comparison_mode,
        rx.vstack(
            rx.heading("📊 Scenario Comparison", size="lg"),
            rx.cond(
                len(MortgageState.scenarios) >= 2,
                rx.vstack(
                    rx.text("Select scenarios to compare:"),
                    rx.checkbox_group(
                        rx.foreach(
                            MortgageState.scenarios,
                            lambda name: rx.checkbox(name, value=name),
                        ),
                        value=MortgageState.selected_scenarios,
                        on_change=MortgageState.set_selected_scenarios,
                    ),
                    # Comparison charts and tables would go here
                    spacing="4",
                ),
                rx.text("Save at least 2 scenarios to enable comparison"),
            ),
            spacing="4",
            width="100%",
        ),
    )
```

### 7. Main Application (mortgage_calculator.py)
```python
import reflex as rx
from .state import MortgageState
from .components import inputs, outputs, charts, comparison

def index() -> rx.Component:
    """Main application layout."""
    return rx.hstack(
        # Sidebar
        inputs.sidebar(),
        
        # Main content
        rx.vstack(
            outputs.error_display(),
            outputs.metrics_dashboard(),
            charts.charts_section(),
            outputs.amortization_table(),
            comparison.scenario_manager(),
            comparison.comparison_dashboard(),
            spacing="6",
            padding="6",
            width="100%",
            overflow_y="auto",
        ),
        width="100%",
        height="100vh",
        spacing="0",
    )

# Create the app
app = rx.App(
    state=MortgageState,
    style={
        "font_family": "Inter, sans-serif",
        "background_color": "#f9fafb",
    },
)

app.add_page(index, route="/", title="Mortgage Calculator")
```

### 8. Styling (styles/styles.py)
```python
import reflex as rx

# Design system colors
COLORS = {
    "primary": "#1e3a8a",
    "secondary": "#10b981",
    "accent": "#f59e0b",
    "background": "#f9fafb",
    "text": "#374151",
    "error": "#ef4444",
    "white": "#ffffff",
    "gray_100": "#f3f4f6",
    "gray_200": "#e5e7eb",
    "gray_600": "#6b7280",
    "gray_900": "#111827",
}

# Component styles
button_style = {
    "border_radius": "0.375rem",
    "font_weight": "medium",
    "transition": "all 0.2s",
    "_hover": {
        "transform": "translateY(-1px)",
        "shadow": "md",
    },
}

card_style = {
    "padding": "1rem",
    "border_radius": "0.5rem",
    "border": f"1px solid {COLORS['gray_200']}",
    "background_color": COLORS["white"],
    "shadow": "sm",
}

input_style = {
    "border_radius": "0.375rem",
    "border": f"1px solid {COLORS['gray_200']}",
    "_focus": {
        "border_color": COLORS["primary"],
        "shadow": f"0 0 0 3px {COLORS['primary']}20",
    },
}
```

## Deployment

### Local Development
```bash
# Install Reflex
pip install reflex

# Initialize project
reflex init

# Run development server
reflex run
```

### Production Deployment
```bash
# Build for production
reflex export

# Deploy to hosting service (Vercel, Netlify, etc.)
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN reflex export

EXPOSE 3000 8000

CMD ["reflex", "run", "--env", "prod"]
```

This Reflex-specific plan provides a complete implementation using Reflex's reactive state management, component-based architecture, and modern Python web development patterns.