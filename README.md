# Mortgage Calculator - Streamlit Application

A comprehensive mortgage calculator web application built with Streamlit that allows users to adjust mortgage parameters, visualize payment scenarios, and compare multiple configurations.

## Features

### Core Functionality
- **Dynamic Mortgage Calculations**: Based on the existing `calculate_monthly_payment` function
- **Interactive Parameter Adjustment**: Real-time updates as you modify inputs
- **Multiple Interest Rate Periods**: Support for varying interest rates over time
- **Refinancing Analysis**: Model the impact of refinancing strategies
- **Additional Payment Options**: See how extra payments reduce interest and time

### Key Outputs
- **Payoff Timeline**: Displayed in "Years Months" format
- **Total Interest Paid**: Sum of all interest payments over loan term
- **Total Amount Paid**: Principal + total interest
- **Average Monthly Payment**: Total paid ÷ total months

### Visualizations
- **Payment Timeline Chart**: Principal vs interest payments over time
- **Loan Balance Chart**: Remaining balance trajectory with milestones
- **Interest vs Principal Chart**: Cumulative comparison
- **Annual Summary Chart**: Year-by-year payment breakdown

### Advanced Features
- **Multi-Scenario Comparison**: Compare 2-4 different mortgage configurations
- **Scenario Management**: Save, load, and manage different parameter sets
- **Amortization Schedule**: Complete month-by-month payment table with export
- **Smart Recommendations**: Automated insights based on your scenarios
- **Data Export**: Download amortization schedules and comparisons as CSV

## Installation

### Using uv (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd mortgage-calculator-streamlit-cursor

# Install dependencies with uv
uv pip install streamlit pandas plotly numpy streamlit-option-menu streamlit-plotly-events
```

### Using pip
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install streamlit pandas plotly numpy streamlit-option-menu streamlit-plotly-events
```

## Running the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## Usage Guide

### 1. Configure Your Mortgage
Use the sidebar to set:
- **Loan Amount**: Use slider or direct input
- **Loan Term**: Years for the mortgage
- **Interest Rates**: Add multiple rates for different periods
- **Payment Settings**: Minimum and additional monthly payments
- **Refinancing Options**: Enable and configure refinancing parameters

### 2. View Results
The main dashboard displays:
- Key metrics cards showing payoff time, total interest, etc.
- Interactive charts with multiple visualization options
- Detailed amortization schedule with filtering and export
- Annual summary breakdown

### 3. Compare Scenarios
1. Save your current configuration as a named scenario
2. Adjust parameters and save additional scenarios
3. Click "Compare Scenarios" to see side-by-side analysis
4. View recommendations for the best option based on your priorities

## Project Structure

```
mortgage-calculator-streamlit-cursor/
├── app.py                    # Main Streamlit application
├── logic.py                  # Core calculation logic
├── components/               # UI components
│   ├── inputs.py            # Input widgets
│   ├── outputs.py           # Results display
│   ├── charts.py            # Visualizations
│   └── comparison.py        # Multi-scenario comparison
├── utils/                   # Utility functions
│   ├── helpers.py          # Helper functions
│   └── formatters.py       # Number/currency formatting
├── config/                  # Configuration
│   └── settings.py         # App settings and defaults
└── styles/                  # Styling
    └── style.css           # Custom CSS
```

## Input Parameters

- **Loan Amount**: $10,000 - $10,000,000
- **Loan Term**: 5 - 50 years
- **Interest Rates**: 0.1% - 20% (multiple periods supported)
- **Minimum Payment**: Optional minimum monthly payment
- **Additional Payment**: Extra monthly payment to reduce principal
- **Refinancing Options**:
  - Refinance cycle (years)
  - Principal threshold for refinancing
  - Expected rate increase after refinancing

## Design Features

- **Professional Theme**: Navy blue primary color with green accents
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Interactive Charts**: Hover for details, zoom, and pan
- **Data Tables**: Sortable, filterable with pagination
- **Export Options**: Download data as CSV for further analysis

## Tips for Best Results

1. **Start Simple**: Begin with basic parameters before enabling refinancing
2. **Save Scenarios**: Create scenarios for different strategies (e.g., "Conservative", "Aggressive", "With Extra Payments")
3. **Compare Options**: Use the comparison feature to see which strategy saves the most
4. **Export Data**: Download amortization schedules for detailed analysis
5. **Consider Reality**: Remember to factor in real-world considerations like fees and market conditions

## Dependencies

- streamlit >= 1.28.0
- pandas >= 1.5.0
- plotly >= 5.0.0
- numpy >= 1.24.0
- streamlit-option-menu
- streamlit-plotly-events

## License

This project is provided as-is for educational and personal use.

## Acknowledgments

Built with Streamlit and based on the mortgage calculation logic in `logic.py`. 