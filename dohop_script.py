import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import log

# retry request up to five times if 500/503 status codes are returned
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 503])
session.mount('https://', HTTPAdapter(max_retries=retries))
ticketing_data_sources = ['gatwick-connect', 'dohop-connect', 'easyjet-connect']


def requests_get(url):
    request = requests.Request('GET', url, params={'ticketing-partner': '36fd0d405f4541b7be72d117b574a70f'})
    prepared = request.prepare()
    log.log_raw_request(prepared, 'dohop')
    response = session.send(prepared)
    log.log_raw_response(response, 'dohop')
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        return None


def get_available_flights(city_from, city_to, date_departure, date_return):
    tickets = []
    url_pattern = 'https://partners-api.dohop.com/api/v2/ticketing/{}/DE/EUR/{}/{}/{}'
    data_departure_formatted = date_departure.strftime('%Y-%m-%d')
    date_return_formatted = None
    if date_return:
        date_return_formatted = date_return.strftime('%Y-%m-%d')
        url_pattern += '/{}'
    for data_source in ticketing_data_sources:
        tickets_per_datasource = requests_get(url_pattern.format(
            data_source, city_from,
            city_to,
            data_departure_formatted,
            date_return_formatted))
        if tickets_per_datasource and 'itineraries' in tickets_per_datasource:
            tickets.extend(tickets_per_datasource['itineraries'])
    return tickets

