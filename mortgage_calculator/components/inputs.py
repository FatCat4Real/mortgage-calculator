import reflex as rx
from ..state import MortgageState

def loan_inputs() -> rx.Component:
    """Render loan amount and term inputs."""
    return rx.vstack(
        rx.heading("💰 Loan Details", size="4"),
        rx.hstack(
            rx.vstack(
                rx.text("Loan Amount ($)"),
                rx.input(
                    value=MortgageState.loan_amount,
                    on_change=MortgageState.set_loan_amount_str,
                    type="number",
                    min="10000",
                    max="10000000",
                    step="10000",
                ),
                width="50%",
            ),
            rx.vstack(
                rx.text("Loan Term (Years)"),
                rx.input(
                    value=MortgageState.years,
                    on_change=MortgageState.set_years_str,
                    type="number",
                    min="5",
                    max="50",
                ),
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
        rx.heading("📈 Interest Rates", size="4"),
        rx.hstack(
            rx.text("Interest Rates: "),
            rx.foreach(
                MortgageState.interest_rates,
                lambda rate: rx.text(f"{rate}%, "),
            ),
        ),
        rx.hstack(
            rx.text("Add Rate:"),
            rx.button(
                "➕ Add 5.0%", 
                on_click=lambda: MortgageState.add_interest_rate(5.0),
                size="2",
            ),
            spacing="2",
        ),
        spacing="2",
        width="100%",
    )

def payment_inputs() -> rx.Component:
    """Render payment settings inputs."""
    return rx.vstack(
        rx.heading("💳 Payment Settings", size="4"),
        rx.hstack(
            rx.vstack(
                rx.text("Minimum Monthly Payment ($)"),
                rx.input(
                    value=MortgageState.minimum_monthly_payment,
                    on_change=MortgageState.set_minimum_monthly_payment_str,
                    type="number",
                    min="0",
                    step="100",
                ),
                width="50%",
            ),
            rx.vstack(
                rx.text("Additional Monthly Payment ($)"),
                rx.input(
                    value=MortgageState.additional_payment,
                    on_change=MortgageState.set_additional_payment_str,
                    type="number",
                    min="0",
                    step="100",
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
        rx.heading("🔄 Refinancing Options", size="4"),
        rx.checkbox(
            "Enable Refinancing",
            checked=MortgageState.refinance,
            on_change=MortgageState.set_refinance,
        ),
        rx.cond(
            MortgageState.refinance,
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Refinance Every (Years)"),
                        rx.input(
                            value=MortgageState.refinance_every_x_years,
                            on_change=MortgageState.set_refinance_every_x_years_str,
                            type="number",
                            min="1",
                            max="10",
                        ),
                        width="33%",
                    ),
                    rx.vstack(
                        rx.text("Principal Threshold ($)"),
                        rx.input(
                            value=MortgageState.refinance_when_principal_hit,
                            on_change=MortgageState.set_refinance_when_principal_hit_str,
                            type="number",
                            min="100000",
                            step="100000",
                        ),
                        width="33%",
                    ),
                    rx.vstack(
                        rx.text("Rate Increase (%)"),
                        rx.input(
                            value=MortgageState.refinance_interest_will_increase,
                            on_change=MortgageState.set_refinance_interest_will_increase_str,
                            type="number",
                            min="0.0",
                            max="5.0",
                            step="0.1",
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
            size="3",
            color_scheme="blue",
        ),
        spacing="6",
        padding="4",
        width="350px",
        height="100vh",
        overflow_y="auto",
        border_right="1px solid #e2e8f0",
    )