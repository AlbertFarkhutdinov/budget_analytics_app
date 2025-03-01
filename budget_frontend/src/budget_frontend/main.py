import requests
import streamlit as st

API_BASE_URL = 'http://127.0.0.1:8000'


def get_headers():
    bearer_token = st.session_state.get('token', '')
    return {'Authorization': f'Bearer {bearer_token}'}


def main():
    # Authentication
    st.title('Budget Analytics')
    st.sidebar.title('Authentication')
    username = st.sidebar.text_input('Username')
    password = st.sidebar.text_input('Password', type='password')
    if st.sidebar.button('Login'):
        response = requests.post(
            url=f'{API_BASE_URL}/auth/login',
            json={'username': username, 'password': password},
        )
        if response.status_code == 200:
            token = response.json()['access_token']
            st.session_state['token'] = token
            st.sidebar.success('Logged in successfully')
        else:
            st.sidebar.error('Login failed')

    # Data Entry Form
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
            headers=get_headers(),
        )
        if response.status_code == 200:
            st.success('Entry added successfully')
        else:
            st.error('Failed to add entry')

    # View Budget Entries
    st.header('Budget Entries')
    if st.button('Load Entries'):
        response = requests.get(
            url=f'{API_BASE_URL}/entries/',
            headers=get_headers(),
        )
        if response.status_code == 200:
            entries = response.json()
            st.table(entries)
        else:
            st.error('Failed to load entries')


if __name__ == '__main__':
    main()
