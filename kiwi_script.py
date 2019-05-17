import requests
import json
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from datetime import datetime
from pprint import pprint as pp
import log


# retry request up to five times if 500/503 status codes are returned
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 503])
session.mount('https://', HTTPAdapter(max_retries=retries))
ticketing_data_sources = ['gatwick-connect', 'dohop-connect', 'easyjet-connect']


def requests_get(url):
    request = requests.Request('GET', url, params={'partner':'picky'})
    prepared = request.prepare()
    log.log_raw_request(prepared, 'kiwi')
    response = session.send(prepared)
    log.log_raw_response(response, 'kiwi')
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        return None


def get_all_flights(response):
    pp(response.keys())
    pp(response['currency'])
    itineraries = response['data']
    return itineraries


def get_all_available_tickets_and_currency_code(city_from, city_to, date_departure, date_return):
    data_departure_formatted = date_departure.strftime('%d/%m/%Y')
    url_pattern = 'https://api.skypicker.com/flights?flyFrom={}&to={}&dateFrom={}&dateTo={}'
    date_return_formatted = None
    if date_return:
        date_return_formatted = date_return.strftime('%d/%m/%Y')
        url_pattern += '&returnFrom={}&returnTo={}'
    response = requests_get(
        url_pattern.format(
            city_from, city_to, data_departure_formatted, data_departure_formatted, date_return_formatted, date_return_formatted))
    if response and 'data' in response and 'currency' in response:
        return response['data'], response['currency']
    else:
        return [], None
