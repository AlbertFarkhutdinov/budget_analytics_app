import sys
from streamlit.web import cli as stcli


def main():
    sys.argv = [
        "streamlit",
        "run",
        "src/budget_frontend/main.py",
        "--server.port",
        "8501",
    ]
    stcli.main()


if __name__ == "__main__":
    main()
