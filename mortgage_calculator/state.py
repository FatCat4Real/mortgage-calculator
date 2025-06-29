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
    
    def set_loan_amount_str(self, value: str):
        """Set loan amount from string input."""
        try:
            self.loan_amount = int(value) if value else 0
            self.calculate()
        except ValueError:
            pass
    
    def set_years_str(self, value: str):
        """Set years from string input."""
        try:
            self.years = int(value) if value else 1
            self.calculate()
        except ValueError:
            pass
    
    def set_minimum_monthly_payment_str(self, value: str):
        """Set minimum monthly payment from string input."""
        try:
            self.minimum_monthly_payment = int(value) if value else 0
            self.calculate()
        except ValueError:
            pass
    
    def set_additional_payment_str(self, value: str):
        """Set additional payment from string input."""
        try:
            self.additional_payment = int(value) if value else 0
            self.calculate()
        except ValueError:
            pass
    
    def set_refinance_every_x_years_str(self, value: str):
        """Set refinance years from string input."""
        try:
            self.refinance_every_x_years = int(value) if value else 3
            self.calculate()
        except ValueError:
            pass
    
    def set_refinance_when_principal_hit_str(self, value: str):
        """Set refinance principal threshold from string input."""
        try:
            self.refinance_when_principal_hit = int(value) if value else 3_000_000
            self.calculate()
        except ValueError:
            pass
    
    def set_refinance_interest_will_increase_str(self, value: str):
        """Set refinance interest increase from string input."""
        try:
            self.refinance_interest_will_increase = float(value) if value else 1.0
            self.calculate()
        except ValueError:
            pass

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
        if rate > 0:
            self.interest_rates.append(rate)
            self.calculate()
    
    def remove_interest_rate(self, index: int):
        """Remove interest rate at given index."""
        if 0 <= index < len(self.interest_rates) and len(self.interest_rates) > 1:
            self.interest_rates.pop(index)
            self.calculate()
    
    def update_interest_rate(self, index: int, rate: float):
        """Update interest rate at given index."""
        if 0 <= index < len(self.interest_rates) and rate > 0:
            self.interest_rates[index] = rate
            self.calculate()
    
    def save_scenario(self, name: str):
        """Save current parameters as a scenario."""
        if name and name.strip():
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