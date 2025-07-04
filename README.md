# Mortgage Calculator

This is a Streamlit web application for calculating and comparing mortgage scenarios.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd mortgage-calculator
    ```

2.  **Create a virtual environment:**
    It is recommended to use a virtual environment.

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies using uv:**
    This project uses `uv` for package management.
    ```bash
    pip install uv
    uv pip install -r requirements.txt
    ```
    *Note: A `requirements.txt` will be generated in the next step. If you have the `pyproject.toml` you can run `uv pip install -r requirements.txt` or `uv pip sync`.*

## Running the application

To run the Streamlit app, use the following command:

```bash
uv run streamlit run app.py
```

The application should open in your web browser. 