import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt

from frontend.api.reports_api_client import ReportsAPIClient


class ReportsPage:

    def __init__(self) -> None:
        self.api = ReportsAPIClient()

    def run(self) -> None:
        """Run the Streamlit app."""
        st.title('Budget Reports')

        report_types = {
            'expenses_per_day': 'Expenses Per Day',
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
            st.write('### Last Generated Report')
            table_data = last_report.get('table_data')
            if table_data is not None:
                df = pd.DataFrame(table_data)
                st.table(df)
            plot_data = last_report.get('plot_data')
            if plot_data is not None:
                fig, ax = plt.subplots()
                plt.plot(plot_data['x'], plot_data['y'])
                ax.set_title(report_name)
                st.pyplot(fig)
