import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)


@app.route('/')
def home():
    return {'cimb': get_cimb_rates()}


def get_cimb_rates():
    cimb_url = 'https://www.cimbclicks.com.sg/sgd-to-myr'
    # User-Agent is required to prevent 403 Forbidden error
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0'
    }
    r = requests.get(cimb_url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')

    valid = False
    rate = ''
    # The rate value is found in the first input of first form
    for form in soup.find_all('form'):
        first_input = form.find('input')

        if first_input:
            value = first_input.get('value')
            value = value.replace('[', '')
            value = value.replace(']', '')
            try:
                rate = float(value)
                valid = True
                break
            except ValueError:
                pass

    return rate if valid else 'N/A'


# res = get_cimb_rates()
# print(res)
