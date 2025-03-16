import sys

from streamlit.web import cli as stcli


def start_frontend():
    sys.argv = [
        "streamlit",
        "run",
        "src/budget_analytics_app/frontend/entries.py",
        "--server.port",
        "8501",
    ]
    stcli.main()


if __name__ == "__main__":
    start_frontend()
