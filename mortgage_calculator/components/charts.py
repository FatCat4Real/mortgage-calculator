import reflex as rx
from ..state import MortgageState

def payment_timeline_chart() -> rx.Component:
    """Payment timeline chart showing principal vs interest."""
    return rx.vstack(
        rx.heading("Payment Timeline", size="4"),
        rx.cond(
            MortgageState.calculation_result,
            rx.box(
                rx.text("Payment timeline chart will display here"),
                height="300px",
                width="100%",
                border="1px solid #e2e8f0",
                border_radius="lg",
                padding="4",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.text("No data to display"),
        ),
        spacing="4",
        width="100%",
    )

def loan_balance_chart() -> rx.Component:
    """Loan balance over time chart."""
    return rx.vstack(
        rx.heading("Loan Balance", size="4"),
        rx.cond(
            MortgageState.calculation_result,
            rx.box(
                rx.text("Loan balance chart will display here"),
                height="300px",
                width="100%",
                border="1px solid #e2e8f0",
                border_radius="lg",
                padding="4",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.text("No data to display"),
        ),
        spacing="4",
        width="100%",
    )

def charts_section() -> rx.Component:
    """Charts section with tabs."""
    return rx.vstack(
        rx.heading("📈 Visualizations", size="5"),
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Payment Timeline", value="payment"),
                rx.tabs.trigger("Loan Balance", value="balance"),
            ),
            rx.tabs.content(
                payment_timeline_chart(),
                value="payment",
            ),
            rx.tabs.content(
                loan_balance_chart(),
                value="balance",
            ),
            default_value="payment",
        ),
        spacing="4",
        width="100%",
    )