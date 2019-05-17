import dohop_script
import Ticket
import kiwi_script


def get_available_ticket_list(city_from, city_to, date_departure, date_return):
    dohop_tickets_raw = dohop_script.get_available_flights(city_from, city_to, date_departure, date_return)
    kiwi_tickets_raw, kiwi_currency = kiwi_script.get_all_available_tickets_and_currency_code(city_from, city_to, date_departure, date_return)
    tickets_list = []
    for dohop_ticket_raw in dohop_tickets_raw:
        tickets_list.append(Ticket.DohopTicket(dohop_ticket_raw))

    for kiwi_ticket_raw in kiwi_tickets_raw:
        tickets_list.append(Ticket.KiwiTicket(kiwi_ticket_raw, kiwi_currency))
    return tickets_list


def get_cheapest_ticket(ticket_list):
    if not ticket_list:
        return None
    cheapest_ticket = min(ticket_list, key= Ticket.get_price)
    return cheapest_ticket


def get_sorted_tickets_by_departure_time(tickets_list):
    sorted_list = sorted(tickets_list, key=Ticket.get_departure_time)
    return sorted_list
