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


def requests_get(url):
    request = requests.Request('GET', url, params={'ticketing-partner': '36fd0d405f4541b7be72d117b574a70f'})
    prepared = request.prepare()
    log_raw_request(prepared)
    response = session.send(prepared)
    log_raw_response(response)
    response.raise_for_status()
    return response.json()


def log_raw_request(request):
    with open("api-logs.txt", "a") as file:
        file.write('Request_dohop: {}\n'.format(request.method + ' ' + request.url))
    # print('Request: {}\n'.format(request.method + ' ' + request.url))


def log_raw_response(response):
    with open("api-logs.txt", "a") as file:
        file.write('Response_dohop: {}\n'.format("URL " + response.url + '; STATUS CODE: ' + str(response.status_code)))
    # print('Response: {}\n'.format("URL " + response.url + '; STATUS CODE: ' + str(response.status_code)))


def get_available_flights(data_source, sity_from, sity_to, date_departure, date_return):
    response = requests_get('https://partners-api.dohop.com/api/v2/ticketing/{}/DE/EUR/'
                            '{}/{}/{}/{}'.format(data_source, sity_from, sity_to, date_departure, date_return))
    return response


def get_cheapest_flight(response):
    itineraries = response['itineraries']
    cheapest_ticket = None
    for itinerary in itineraries:
        cheapest_price_in_ticket = None
        for fare_combination in itinerary['fare-combinations']:
            code = fare_combination['fare-including-fee']['currency']
            amount = fare_combination['fare-including-fee']['amount']
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


def get_all_responses(sity_from, sity_to, date_departure, date_return):
    all_responses = []
    for data_source in ticketing_data_sources:
        response = get_available_flights(data_source, sity_from, sity_to, date_departure,
                                         date_return)
        all_responses.append(response)
    return all_responses


# This function helps to find the cheapest tickets in ticketing_data_sources
# (in each: 'gatwick-connect', 'dohop-connect', 'easyjet-connect')
# then it returns information (flight details and price in json) about one cheapest ticket
# from previous result. So we get information where we can find the cheapest ticket
# in 'gatwick-connect', 'dohop-connect' or'easyjet-connect'.
def find_cheapest_ticket_from_all_data_sources(all_responses):
    all_json_data = []
    for response in all_responses:
        cheapest_flight = get_cheapest_flight(response)
        formated_cheapest_flight_JSON = formate_data_in_JSON(cheapest_flight)
        all_json_data.append(formated_cheapest_flight_JSON)
    lowest_price = None
    cheapest_flight_from_all_data_sources = None
    for item in all_json_data:
        if lowest_price:
            if item['price'] < lowest_price:
                lowest_price = item['price']
                cheapest_flight_from_all_data_sources = item
        else:
            lowest_price = item['price']
            cheapest_flight_from_all_data_sources = item
    return cheapest_flight_from_all_data_sources


def formate_data_in_JSON(cheapest_ticket):
    itinerary = {}
    itinerary['price'] = cheapest_ticket['cheapest_price']
    itinerary['flight_details'] = {}
    itinerary['flight_details']['flights-out'] = []
    for flight in cheapest_ticket['flights-out']:
        flight = flight[0]
        itinerary['flight_details']['flights-out'].append({
                        'departure_airport': flight[0],
                        'arrival_airport': flight[1],
                        'departure_date': flight[3][:10],
                        'arrival_date': flight[4][:10],
                        'departure_time': flight[3][11:],
                        'arrival_time': flight[4][11:],
                        'flight_number': flight[2],
        })
    if 'flights-home' in cheapest_ticket:
        itinerary['flight_details']['flights-home'] = []
        for flight in cheapest_ticket['flights-home']:
            flight = flight[0]
            itinerary['flight_details']['flights-home'].append({
                'departure_airport': flight[0],
                'arrival_airport': flight[1],
                'departure_date': flight[3][:10],
                'arrival_date': flight[4][:10],
                'departure_time': flight[3][11:],
                'arrival_time': flight[4][11:],
                'flight_number': flight[2],
            })
    return itinerary


if __name__ == '__main__':
    parameters = "EDI", "NCE", "2019-08-01", "2019-08-19"

    all_responses = get_all_responses("EDI", "NCE", "2019-08-01", "2019-08-19")
    # print(type(all_responses))

    pp(find_cheapest_ticket_from_all_data_sources(all_responses))

