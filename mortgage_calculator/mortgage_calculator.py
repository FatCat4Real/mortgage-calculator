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
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        scaling="100%",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)

app.add_page(index, route="/", title="Mortgage Calculator")