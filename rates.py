import requests
from bs4 import BeautifulSoup
from flask import Flask, request
from flask_cors import CORS
from requests.exceptions import RequestException

app = Flask(__name__)

# CORS(app)
CORS(app, resources={r"/*": {
    "origins": [
        "http://yongjianwen-static.s3-website-ap-southeast-1.amazonaws.com/",
        "http://127.0.0.1:5500"
    ]
}})


@app.route('/rates')
def rates():
    sgd = request.form.get('sgd', 1000)
    return {
        'cimb': get_cimb_rates(sgd),
        'wise': get_wise_rates(sgd)
    }


def get_cimb_rates(sgd):
    res = -1

    try:
        cimb_url = 'https://www.cimbclicks.com.sg/sgd-to-myr'
        # User-Agent is required to prevent 403 Forbidden error
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0'
        }
        r = requests.get(cimb_url, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')

        # The rate value is found in the first input of first form
        for form in soup.find_all('form'):
            first_input = form.find('input')

            if first_input:
                value = first_input.get('value')
                value = value.replace('[', '')
                value = value.replace(']', '')
                try:
                    res = float(value) * sgd
                    break
                except ValueError:
                    pass
    except RequestException as e:
        print(e)

    return res


def get_wise_rates(sgd):
    res = -1

    try:
        wise_url = 'https://wise.com/gateway/v1/guest-send-sessions'
        data = {
            "capabilities": None,
            "configuration": "SEND_MONEY_PRICING_PAGE",
            "presets": {
                "sourceCurrency": "SGD",
                "targetCurrency": "MYR",
                "payInCountry": "sg",
                "profileType": "PERSONAL"
            }
        }
        r = requests.post(wise_url, json=data)
        session_id = r.json().get('id')

        if session_id:
            wise_url = f'https://wise.com/gateway/v1/guest-send-sessions/{session_id}/calculator'
            data = {
                "version": 1,
                "supportedComponents": [
                    {
                        "name": "HIGH_VOLUME_FEE_ADJUSTMENTS_EDUCATION",
                        "version": 1
                    }
                ],
                "capabilities": [
                    {
                        "name": "FEE_ADJUSTMENTS",
                        "version": 1
                    }
                ]
            }
            # Need to call this first before updating amount
            requests.post(wise_url, json=data)

            wise_url = f'https://wise.com/gateway/v1/guest-send-sessions/{session_id}/calculator/action'
            data = {"action": "UPDATE_SOURCE_AMOUNT", "value": {"amount": sgd}, "version": 1}
            r = requests.post(wise_url, json=data)
            res = r.json().get('target').get('current').get('amount')
    except RequestException as e:
        print(e)
    except AttributeError as e:
        print(e)

    return res


if __name__ == '__main__':
    print(rates())
