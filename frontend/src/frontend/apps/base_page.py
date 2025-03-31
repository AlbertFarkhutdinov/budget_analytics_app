"""
The module that provides the base Streamlit page.

It contains the `BasePage` class which is designed
to handle responses from the backend service
and display relevant messages to the user through Streamlit.

"""
import streamlit as st


class BasePage:
    """A class to handle responses and display messages through Streamlit."""

    @classmethod
    def handle_response(cls, response: dict[str, str]) -> int:
        """
        Process the given response and display appropriate messages.

        Parameters
        ----------
        response : dict
            A dictionary containing 'detail' or 'message' keys.
            - 'detail': Error message to display if an error occurs.
            - 'message': Success message to display
            if the operation is successful.

        Returns
        -------
        int
            A status code based on the response:
            - 1 if the operation is successful (message is displayed).
            - -1 if the operation failed (error is displayed).
            - 0 if neither message nor error is present.

        """
        detail = response.get('detail', '')
        if detail:
            st.error(detail)
            return -1
        message = response.get('message', '')
        if message:
            st.success(message)
            return 1
        return 0
