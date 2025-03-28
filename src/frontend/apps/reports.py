import streamlit as st
from plotly import express as px

from frontend.api.api_client import ReportsType
from frontend.api.reports_api_client import ReportsAPIClient
from frontend.apps.base_page import BasePage


class ReportsPage(BasePage):

    def __init__(self) -> None:
        self.api = ReportsAPIClient()

    def run(self) -> None:
        """Run the Streamlit app."""
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
        if st.button(f'Generate {report_name}'):
            report_data = self.api.generate_report(report_type)
            self._handle_response(response=report_data)
            if 'detail' in report_data:
                st.error('Failed to generate report.')
            else:
                st.success('Report generated successfully.')

    def _load_report(
        self,
        report_name: str,
        report_type: str,
    ) -> None:
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
