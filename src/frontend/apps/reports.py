import streamlit as st

from frontend.api.reports_api_client import ReportsAPIClient


class ReportsPage:

    def __init__(self) -> None:
        self.api = ReportsAPIClient()

    def run(self) -> None:
        """Run the Streamlit app."""
        st.title('Budget Reports')
