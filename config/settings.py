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

# Format settings
CURRENCY_FORMAT = "${:,.0f}"
PERCENTAGE_FORMAT = "{:.1f}%" 