"""
The module that provides the Streamlit page for managing budget reports.

It contains the `ReportsPage` class, which handles the user interface
and logic for generating and displaying budget reports.

"""
import streamlit as st
from plotly import express as px

from frontend.api.api_client import ReportsType
from frontend.api.reports_api_client import ReportsAPIClient
from frontend.apps.base_page import BasePage


class ReportsPage(BasePage):
    """
    A class to handle the UI and logic for generating and displaying reports.

    Attributes
    ----------
    api : ReportsAPIClient
        API client for budget reports.

    Methods
    -------
    run() -> None
        Run the budget reports page UI.

    """

    def __init__(self) -> None:
        """Initialize the `ReportsPage` instance."""
        self.api = ReportsAPIClient()

    def run(self) -> None:
        """
        Run the budget reports page UI.

        This method allows the user to generate and view reports
        for the following types of budget data:
         - Expenses Per Category;
         - Expenses Per Time Interval.

        """
        st.title('Budget Reports')
        report_types = {
            'expenses_per_category': 'Expenses Per Category',
            'expenses_per_interval': 'Expenses Per Time Interval',
        }
        for report_type, report_name in report_types.items():
            st.subheader(report_name)
            self._generate_report(
                report_name=report_name,
                report_type=report_type,
            )
            self._load_report(
                report_name=report_name,
                report_type=report_type,
            )

    def _generate_report(
        self,
        report_name: str,
        report_type: str,
    ) -> None:
        """
        Generate a report based on the provided report name and type.

        This method is triggered when the "Generate Report" button is clicked.
        It fetches the report data and displays a success or error message.

        Parameters
        ----------
        report_name : str
            The name of the report that is displayed on the button.
        report_type : str
            The type of the report that is sent in a generation request.

        """
        if st.button(f'Generate {report_name}'):
            report_data = self.api.generate_report(report_type)
            self.handle_response(response=report_data)
            if 'detail' in report_data:
                st.error('Failed to generate report.')
            else:
                st.success('Report generated successfully.')

    def _load_report(
        self,
        report_name: str,
        report_type: str,
    ) -> None:
        """
        Load and display the last generated report for the specified type.

        If no report is found, the user is prompted to generate a new one.
        Otherwise, the last report is displayed with appropriate plotting.

        Parameters
        ----------
        report_name : str
            The name of the report that is displayed on the button.
        report_type : str
            The type of the report that is sent in a generation request.

        """
        last_report = self.api.load_last_report(report_type)
        if 'detail' in last_report:
            st.info('No report found. Generate one first.')
            return
        st.write('#### Last Generated Report')
        if last_report is not None:
            method = getattr(self, f'_plot_{report_type}', None)
            if method is None:
                st.error(f'Report "{report_name}" is not supported.')
            else:
                method(last_report)

    @classmethod
    def _plot_expenses_per_category(cls, reports: ReportsType) -> None:
        """
        Plot a report of expenses per category.

        This method provides interactive options
        for selecting a time interval and the plot type (bar or pie chart),
        then generates the corresponding plot.

        Parameters
        ----------
        reports : ReportsType
            The report data containing categorized expenses.

        """
        time_type = st.radio(
            'Select time interval type:',
            list(reports.keys()),
            key='expenses_per_category__time_type',
        )
        time_interval = st.selectbox(
            'Select time interval:',
            list(reports[time_type].keys()),
        )
        plot_type = st.radio(
            'Select plot type:',
            ['Bar Chart', 'Pie Chart'],
            key='expenses_per_category__plot_type',
        )
        categories = reports[time_type][time_interval]['category']
        amounts = reports[time_type][time_interval]['amount']

        if plot_type == 'Bar Chart':
            fig = px.bar(
                x=categories,
                y=amounts,
                labels={'x': 'Category', 'y': 'Amount'},
                title=f'Expenses for {time_interval}',
            )
        else:
            fig = px.pie(
                names=categories,
                values=amounts,
                title=f'Expenses for {time_interval}',
            )
        st.plotly_chart(fig)

    @classmethod
    def _plot_expenses_per_interval(cls, reports: ReportsType) -> None:
        """
        Plot a report of expenses per time interval for a selected category.

        This method allows the user to select a category and time interval,
        then generates a bar chart displaying the corresponding expenses.

        Parameters
        ----------
        reports : ReportsType
            The report data containing categorized expenses.

        """
        category = st.selectbox(
            'Select category:',
            list(reports.keys()),
        )
        time_type = st.radio(
            'Select time interval type:',
            list(reports[category].keys()),
            key='expenses_per_interval__time_type',
        )
        time_intervals = reports[category][time_type][time_type]
        amounts = reports[category][time_type]['amount']

        fig = px.bar(
            x=time_intervals,
            y=amounts,
            labels={'x': 'Time Interval', 'y': 'Amount'},
            title=f'Expenses for {category}',
        )
        st.plotly_chart(fig)
