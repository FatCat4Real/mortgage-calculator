import reflex as rx
from ..state import MortgageState

def scenario_manager() -> rx.Component:
    """Scenario management interface."""
    return rx.vstack(
        rx.heading("🔍 Scenario Management", size="5"),
        rx.hstack(
            rx.button(
                "💾 Save Default Scenario",
                on_click=lambda: MortgageState.save_scenario("Default"),
            ),
            spacing="2",
        ),
        rx.text("Scenarios will be saved here"),
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
            rx.heading("📊 Scenario Comparison", size="5"),
            rx.text("Comparison features will be available here"),
            spacing="4",
            width="100%",
        ),
    )