# import pandas as pd
import streamlit as st
# from plotly import express as px

from frontend.api.reports_api_client import ReportsAPIClient


class ReportsPage:

    def __init__(self) -> None:
        self.api = ReportsAPIClient()

    def run(self) -> None:
        """Run the Streamlit app."""
        st.title('Budget Reports')

        report_types = {
            'expenses_per_category': 'Expenses Per Category',
            'expenses_per_interval': 'Expenses Per Time Interval',
        }
        for report_key, report_name in report_types.items():
            st.subheader(report_name)
            if st.button(f'Generate {report_name}'):
                report_data = self.api.generate_report(report_key)
                if 'detail' in report_data:
                    st.error('Failed to generate report.')
                else:
                    st.success('Report generated successfully!')

            last_report = self.api.load_last_report(report_key)
            if 'detail' in last_report:
                st.info('No report found. Generate one first.')
                continue
            st.write('#### Last Generated Report')
            if last_report is not None:
                print(last_report)
                # TODO add plots for reports
                # fig = px.line(x=last_report['x'], y=last_report['y'])
                # fig.update_layout(title_text=report_name)
                # st.plotly_chart(fig)
