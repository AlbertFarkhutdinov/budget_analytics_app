import sys

from streamlit.web import cli as stcli


def start_frontend() -> None:
    sys.argv = [
        'streamlit',
        'run',
        'src/frontend/entries.py',
        '--server.port',
        '8501',
    ]
    stcli.main()


if __name__ == '__main__':
    start_frontend()
