import requests
import streamlit as st

API_BASE_URL = 'http://127.0.0.1:8000'


class BudgetAnalyticsApp:
    def __init__(self):
        self.token = st.session_state.get('token', '')
        self.username = ''
        self.password = ''

    def get_headers(self):
        """Return authorization headers if the user is logged in."""
        if self.token:
            return {'Authorization': f'Bearer {self.token}'}
        return {}

    def _make_request(self, method, endpoint, data=None):
        """Unified method for handling API requests."""
        url = f'{API_BASE_URL}{endpoint}'
        headers = self.get_headers()

        try:
            response = requests.request(
                method=method, 
                url=url, 
                json=data, 
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f'Request failed: {e}')
            return None

    def authenticate_user(self):
        """Handles user authentication via the sidebar."""
        st.sidebar.title('Authentication')
        self.username = st.sidebar.text_input('e-mail')
        self.password = st.sidebar.text_input('password', type='password')

        if st.sidebar.button('Register'):
            self.register()
        if st.sidebar.button('Login'):
            self.login()

    def register(self):
        """Handles user registration."""
        if not self.username or not self.password:
            st.sidebar.error('Username and password cannot be empty.')
            return
        response = self._make_request(
            method='POST',
            endpoint='/auth/register',
            data={
                'username': self.username, 
                'password': self.password,
            })
        if response:
            st.sidebar.success(
                'User registered successfully. Confirm your email.',
            )

    def login(self):
        """Handles user login."""
        response = self._make_request(
            method='POST',
            endpoint='/auth/login',
            data={
                'username': self.username, 
                'password': self.password,
            })
        if response:
            self.token = response.get('access_token')
            if self.token:
                st.session_state['token'] = self.token
                st.sidebar.success('Logged in successfully')
            else:
                st.sidebar.error('Login failed: Invalid response')

    def add_budget_entry(self):
        """Handles adding a budget entry."""
        st.header('Add Budget Entry')
        date = st.date_input('Date')
        shop = st.text_input('Shop')
        product = st.text_input('Product')
        amount = st.number_input('Amount', min_value=0.0)
        category = st.text_input('Category')
        person = st.text_input('Person')
        currency = st.text_input('Currency', value='USD')

        if st.button('Submit Entry'):
            entry = {
                'date': date.strftime('%Y-%m-%d'),
                'shop': shop,
                'product': product,
                'amount': amount,
                'category': category,
                'person': person,
                'currency': currency,
            }
            response = self._make_request(
                method='POST', 
                endpoint='/entries/', 
                data=entry,
            )
            if response:
                st.success('Entry added successfully')

    def view_budget_entries(self):
        """Handles viewing budget entries."""
        st.header('Budget Entries')
        if st.button('Load Entries'):
            entries = self._make_request(
                method='GET',
                endpoint='/entries/',
            )
            if entries:
                st.table(entries)

    def run(self):
        """Runs the Streamlit app."""
        st.title('Budget Analytics')
        self.authenticate_user()
        if self.token:
            self.add_budget_entry()
            self.view_budget_entries()
        else:
            st.warning('Please log in to manage budget entries.')


if __name__ == '__main__':
    app = BudgetAnalyticsApp()
    app.run()
