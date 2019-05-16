"""
NBRB module contains functions necessary to make request to official site of NBRB, get currency rate
and scale to convert price in BYN.
"""


import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 503])
session.mount('https://', HTTPAdapter(max_retries=retries))


def requests_get(url):
    r = session.get(url)
    r.raise_for_status()
    return r.json()


def get_currency_exchange_rate(code):
    #ParamMode=2 in url means that there is a three-digit literal code of the currency (ISO 4217)
    url = 'http://www.nbrb.by/API/ExRates/Rates/{}?ParamMode=2'.format(code)
    response = requests_get(url)
    return response['Cur_OfficialRate'], response['Cur_Scale']


def exchange_currency_into_BYN(code, amount):
    cur_official_rate, cur_scale = get_currency_exchange_rate(code)
    currency_in_BYN = amount / cur_scale * cur_official_rate
    return currency_in_BYN



