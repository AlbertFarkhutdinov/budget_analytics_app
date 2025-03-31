"""
Streamlit Frontend Launcher.

This module provides a function to start the Streamlit frontend application.
It configures the necessary command-line arguments and runs the Streamlit CLI.

"""
import sys

from streamlit.web import cli as stcli

from custom_logging import config_logging

config_logging()


def start_frontend() -> None:
    """
    Start the Streamlit frontend application.

    This function sets the required command-line arguments for Streamlit
    and runs the Streamlit CLI to launch the frontend at the specified port.

    """
    sys.argv = [
        'streamlit',
        'run',
        'src/frontend/main.py',
        '--server.port',
        '8501',
    ]
    stcli.main()


if __name__ == '__main__':
    start_frontend()
