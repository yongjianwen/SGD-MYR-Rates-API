import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

CORS(app)
# CORS(app, resources={r"/*": {"origins": ["https://your-frontend.com"]}}


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

# For development only, do not use for production
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

# res = get_cimb_rates()
# print(res)
