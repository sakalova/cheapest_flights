import requests
import json
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from NBRB import exchange_currency_into_BYN

from pprint import pprint as pp


# retry request up to five times if 500/503 status codes are returned
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 503])
session.mount('https://', HTTPAdapter(max_retries=retries))
ticketing_data_sources = ['gatwick-connect', 'dohop-connect', 'easyjet-connect']

from pprint import pprint

fly_from = 'PRG'
fly_to = 'LGW'
date_from = '18/11/2019'
date_to = '12/12/2019'
url = 'https://api.skypicker.com/flights?flyFrom={}&to={}&dateFrom={}&dateTo={}&partner=picky'.format(fly_from, fly_to, date_from, date_to)


def requests_get(url):
    request = requests.Request('GET', url)
    prepared = request.prepare()
    log_raw_request(prepared)
    response = session.send(prepared)
    log_raw_response(response)
    response.raise_for_status()
    return response.json()


def log_raw_request(request):
    with open("api-logs.txt", "a") as file:
        file.write('Request_kiwi: {}\n'.format(request.method + ' ' + request.url))


def log_raw_response(response):
    with open("api-logs.txt", "a") as file:
        file.write('Response_kiwi: {}\n'.format("URL " + response.url + '; STATUS CODE: ' + str(response.status_code)))


def get_all_flights(response):
    pp(response.keys())
    pp(response['currency'])
    itineraries = response['data']
    return itineraries


def get_cheapest_flight(itineraries):
    cheapest_ticket = None
    for itinerary in itineraries:
        # pp(itinerary)
        cheapest_price_in_ticket = None
        price = itinerary['conversion']
        code = None
        amount = None

        for k,v in price.items():
            code = k
            amount = v
        price_in_BYN = exchange_currency_into_BYN(code, amount)

        if cheapest_price_in_ticket:
            if price_in_BYN < cheapest_price_in_ticket:
                cheapest_price_in_ticket = price_in_BYN

        else:
            cheapest_price_in_ticket = price_in_BYN
        itinerary['cheapest_price'] = cheapest_price_in_ticket
        if cheapest_ticket:
            if cheapest_price_in_ticket < cheapest_ticket['cheapest_price']:
                cheapest_ticket = itinerary
        else:
            cheapest_ticket = itinerary
    return cheapest_ticket


def

response = requests_get(url)
itineraries = get_all_flights(response)
pp(get_cheapest_flight(itineraries))

