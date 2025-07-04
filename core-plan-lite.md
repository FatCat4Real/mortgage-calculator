# Mortgage Calculator Streamlit App Plan

This document outlines the plan to build a simple web application using Streamlit to interact with the mortgage calculation logic.

## Phase 1: Project Setup and Basic UI

1.  **Create application file:**
    -   Create a new file named `app.py`. This will be the main file for the Streamlit application.

2.  **Add dependencies:**
    -   Use `uv` to add `streamlit` and `pandas` to the project dependencies in `pyproject.toml`. Pandas will be useful for handling the data from `calculate_monthly_payment`.

3.  **Build the user interface for inputs:**
    -   In `app.py`, import `streamlit`.
    -   Create a function, say `create_scenario_inputs(scenario_id)`, to house all the input widgets for one scenario. This will help with the comparison feature later.
    -   Use Streamlit widgets for user inputs corresponding to the parameters of `calculate_monthly_payment` function:
        -   `loan`: `st.number_input`
        -   `years`: `st.number_input`
        -   `interest_rates_100`: `st.text_input` (for comma-separated values)
        -   `minimum_monthly_payment`: `st.number_input`
        -   `additional_payment`: `st.number_input`
        -   `refinance`: `st.checkbox`
        -   Conditional inputs for `refinance` options (`refinance_every_x_years`, etc.) that appear only when the checkbox is ticked.
        -   `topup`: `st.checkbox`
        -   Conditional inputs for `topup` options.

## Phase 2: Core Logic and Output

1.  **Integrate calculation logic:**
    -   Import `calculate_monthly_payment` from `logic.py` into `app.py`.
    -   Add a "Calculate" button.

2.  **Perform calculation:**
    -   When the "Calculate" button is pressed, retrieve all the input values from the UI widgets.
    -   Parse the interest rates string into a list of floats.
    -   Call `calculate_monthly_payment` with the user-provided parameters.
    -   Handle potential errors from the calculation function gracefully and display a message to the user.

3.  **Display results:**
    -   Process the dictionary returned by the calculation function.
    -   Calculate the required metrics:
        -   Total loan period (years and months).
        -   Total amount paid.
        -   Total interest paid.
    -   Display these metrics clearly to the user.

## Phase 3: Scenario Comparison

1.  **Enable multiple scenarios:**
    -   Use `st.session_state` to manage a list of scenarios.
    -   Add an "Add Scenario" button. When clicked, it should add a new set of inputs to the UI.
    -   Add a "Remove Scenario" button for each scenario.

2.  **Display side-by-side comparison:**
    -   Use `st.columns` to arrange the scenarios horizontally.
    -   When "Calculate" is clicked, run the calculation for all active scenarios.
    -   Display the inputs and results for each scenario in its own column.

## Phase 4: Final Touches

1.  **Code Refinement:**
    -   Refactor the code for clarity and maintainability. Ensure input-creation and result-display logic is modular.
    -   Add comments where necessary.

2.  **User Experience:**
    -   Add a title and some instructions at the top of the app.
    -   Ensure the layout is clean and easy to understand.
    -   Add data validation with user-friendly error messages (e.g., if interest rates are not entered correctly).

3.  **Documentation:**
    -   Create/update a `README.md` file with instructions on how to install dependencies using `uv` and run the Streamlit application.
