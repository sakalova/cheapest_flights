import tickets_processor
from datetime import datetime
import argparse
from pprint import pprint as pp
import log


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("airport_from", help="the departure location")
    parser.add_argument("airport_to", help="the arrival destination")
    parser.add_argument("departure_date", help="search flights upto this date (YYYY-mm-dd)")
    # "return_date" is optional argument
    parser.add_argument("return_date", help="return date (YYYY-mm-dd)", nargs='?',)
    args = parser.parse_args()
    return args


def main():
    args = create_parser()
    log.reset_file()
    datetime_return = None
    if args.return_date:
        datetime_return = datetime.strptime(args.return_date, '%Y-%m-%d')
    tickets_list = tickets_processor.get_available_ticket_list(args.airport_from, args.airport_to,
                                                               datetime.strptime(args.departure_date, '%Y-%m-%d'), datetime_return)
    if not tickets_list:
        pp('The system didn\'t find any ticket! Try to change dates')
        return 0
    cheapest_ticket = tickets_processor.get_cheapest_ticket(tickets_list)
    pp('-------------cheapest_ticket------------------')
    pp(cheapest_ticket)

    sorted_tickets_list = tickets_processor.get_sorted_tickets_by_departure_time(tickets_list)
    pp('------10 tickets with earliest departures ------')
    pp(sorted_tickets_list[:10])
    print('-------------------------------------------------')



if __name__ == '__main__':
    main()
