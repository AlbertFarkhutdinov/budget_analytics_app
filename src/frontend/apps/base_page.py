import streamlit as st


class BasePage:

    @classmethod
    def _handle_response(cls, response: dict[str, str]) -> int:
        detail = response.get('detail', '')
        if detail:
            st.error(detail)
            return -1
        message = response.get('message', '')
        if message:
            st.success(message)
            return 1
        return 0
