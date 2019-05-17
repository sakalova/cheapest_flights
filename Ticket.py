from datetime import datetime
from NBRB import convert_currency_into_BYN
import json


class Ticket:
    def __init__(self, json_content):
        self.json_content = json_content

    def get_departure_time(self):
        raise NotImplementedError()

    def get_price(self):
        raise NotImplementedError()

    def __repr__(self):
        return str(self.json_content)


class DohopTicket(Ticket):
    def get_departure_time(self):
        return datetime.strptime(self.json_content['flights-out'][0][0][3], '%Y-%m-%d %H:%M')

    def get_price(self):
        if 'best_price_BYN' in self.json_content:
            return self.json_content['best_price_BYN']
        else:
            fare_combinations = self.json_content['fare-combinations']
            cheapest_fare = min(fare_combinations, key=get_price_of_fare)
            self.json_content['best_price_BYN'] = get_price_of_fare(cheapest_fare)
            return self.json_content['best_price_BYN']

    def __repr__(self):
        out_dict = {}
        out_dict['price'] = self.get_price()
        out_dict['flight-details'] = {}
        out_dict['flight-details']['flights-out'] = []
        for flight in self.json_content['flights-out']:
            flight = flight[0]
            out_dict['flight-details']['flights-out'].append({'departure-airport': flight[0],
                                                              'arrival-airport': flight[1],
                                                              'flight-number': flight[2],
                                                              'time-of-departure': flight[3],
                                                              'time-of-arrival': flight[4]})
        if 'flights-home' in self.json_content:
            out_dict['flight-details']['flights-home'] = []
            for flight in self.json_content['flights-home']:
                flight = flight[0]
                out_dict['flight-details']['flights-home'].append({
                    'departure-airport': flight[0],
                    'arrival-airport': flight[1],
                    'flight-number': flight[2],
                    'time-of-departure': flight[3],
                    'time-of-arrival': flight[4]})
        return json.dumps(out_dict, indent=4, sort_keys=True)


def get_price_of_fare(fare):
    return convert_currency_into_BYN(fare['fare-including-fee']['currency'],
                                    fare['fare-including-fee']['amount'])


class KiwiTicket(Ticket):
    def __init__(self, json_content, currency):
        self.json_content = json_content
        self.currency = currency

    def get_departure_time(self):
        return datetime.utcfromtimestamp(self.json_content['dTime'])

    def get_price(self):
        if 'price_in_BYN' in self.json_content:
            return self.json_content['price_in_BYN']
        else:
            price_in_BYN = convert_currency_into_BYN(self.currency, self.json_content['price'])
            self.json_content['price_in_BYN'] = price_in_BYN
            return price_in_BYN

    def __repr__(self):
        out_dict = {}
        out_dict['price'] = self.get_price()
        out_dict['flight-details'] = {}
        out_dict['flight-details']['flights-out'] = []
        for flight in self.json_content['route']:
            time_arrival = datetime.utcfromtimestamp(flight['aTimeUTC']).strftime(
                '%Y-%m-%d %H:%M')

            time_departure = datetime.utcfromtimestamp(flight['dTimeUTC']).strftime(
                '%Y-%m-%d %H:%M')

            flight_details = {'departure-airport': flight['flyFrom'],
                                                              'arrival-airport': flight['flyTo'],
                                                              'flight-number': flight['flight_no'],
                                                              'time-of-departure': time_departure,
                                                              'time-of-arrival': time_arrival}
            if flight['return'] == 0:
                out_dict['flight-details']['flights-out'].append(flight_details)
            else:
                if 'flights-home' not in out_dict['flight-details']:
                    out_dict['flight-details']['flights-home'] = []
                out_dict['flight-details']['flights-home'].append(flight_details)

        return json.dumps(out_dict, indent=4, sort_keys=True)


def get_departure_time(obj):
    return obj.get_departure_time()


def get_price(obj):
    return obj.get_price()

