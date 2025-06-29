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
        box_shadow="sm",
    )

def metrics_dashboard() -> rx.Component:
    """Key metrics dashboard."""
    return rx.vstack(
        rx.heading("📊 Key Metrics", size="5"),
        rx.grid(
            metric_card("Payoff Time", MortgageState.payoff_time, "⏰"),
            metric_card("Total Interest", f"${MortgageState.total_interest:,}", "💰"),
            metric_card("Total Paid", f"${MortgageState.total_paid:,}", "💸"),
            metric_card("Avg Monthly", f"${MortgageState.average_monthly:,}", "📅"),
            columns="4",
            spacing="4",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )

def amortization_table() -> rx.Component:
    """Amortization schedule table."""
    return rx.vstack(
        rx.heading("📋 Amortization Schedule", size="5"),
        rx.cond(
            MortgageState.calculation_result,
            rx.box(
                rx.text("Amortization table will display here after calculation"),
                height="400px",
                width="100%",
                border="1px solid #e2e8f0",
                border_radius="lg",
                padding="4",
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
        rx.callout(
            MortgageState.error_message,
            icon="triangle_alert",
            color_scheme="red",
        ),
    )