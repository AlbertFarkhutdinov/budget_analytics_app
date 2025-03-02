import requests
import streamlit as st

API_BASE_URL = 'http://127.0.0.1:8000'


class BudgetAnalyticsApp:
    def __init__(self):
        self.token = st.session_state.get('token', '')
        self.username = ''
        self.password = ''

    def get_headers(self):
        return {'Authorization': f'Bearer {self.token}'}

    def authenticate_user(self):
        st.sidebar.title('Authentication')
        self.username = st.sidebar.text_input('e-mail')
        self.password = st.sidebar.text_input('password', type='password')

        if st.sidebar.button('Register'):
            self.register()
        if st.sidebar.button('Login'):
            self.login()

    def register(self):
        response = requests.post(
            url=f'{API_BASE_URL}/auth/register',
            json={'username': self.username, 'password': self.password},
        )
        if response.status_code == 200:
            st.sidebar.success(response.json())
        else:
            error_msg = response.json().get("detail", "Unknown error")
            st.sidebar.error(f'Registration failed: {error_msg}')

    def login(self):
        response = requests.post(
            url=f'{API_BASE_URL}/auth/login',
            json={'username': self.username, 'password': self.password},
        )
        if response.status_code == 200:
            self.token = response.json()['access_token']
            st.session_state['token'] = self.token
            st.sidebar.success('Logged in successfully')
        else:
            st.sidebar.error('Login failed')

    def add_budget_entry(self):
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
            response = requests.post(
                url=f'{API_BASE_URL}/entries/',
                json=entry,
                headers=self.get_headers(),
            )
            if response.status_code == 200:
                st.success('Entry added successfully')
            else:
                st.error('Failed to add entry')

    def view_budget_entries(self):
        st.header('Budget Entries')
        if st.button('Load Entries'):
            response = requests.get(
                url=f'{API_BASE_URL}/entries/',
                headers=self.get_headers(),
            )
            if response.status_code == 200:
                entries = response.json()
                st.table(entries)
            else:
                st.error('Failed to load entries')

    def run(self):
        st.title('Budget Analytics')
        self.authenticate_user()
        self.add_budget_entry()
        self.view_budget_entries()


if __name__ == '__main__':
    app = BudgetAnalyticsApp()
    app.run()
