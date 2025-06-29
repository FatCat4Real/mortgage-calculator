"""
Mortgage Calculator - Streamlit Application

A comprehensive mortgage calculator with scenario comparison and visualizations.
"""

import streamlit as st
from components import inputs, outputs, comparison
from utils import helpers
from config.settings import APP_CONFIG
import os


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title=APP_CONFIG['page_title'],
        page_icon=APP_CONFIG['page_icon'],
        layout=APP_CONFIG['layout'],
        initial_sidebar_state=APP_CONFIG['initial_sidebar_state']
    )
    
    # Load custom CSS
    css_path = os.path.join('styles', 'style.css')
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Initialize session state
    helpers.init_session_state()
    
    # Check if we're in comparison mode
    if st.session_state.get('comparison_mode', False):
        # Render comparison view
        comparison.render_comparison()
    else:
        # Render normal view
        # Sidebar inputs
        inputs.render_sidebar()
        
        # Main dashboard
        outputs.render_dashboard()


if __name__ == "__main__":
    main() 