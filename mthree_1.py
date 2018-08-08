"""Model for flight booking management system"""


class Flight:
    """A flight with a particular passenger aircraft."""

    def __init__(self, number, aircraft):
        """Initialise and check form of flight number
        Args:
            number: String that represents the flight number. Takes the form AB1(234)
             where AB is the airline (must be 2 uppercase letters only) and 1234 is
             the flight number that may take a value up to 9999
            aircraft: The aircraft type
            """

        if not number[:2].isalpha():
            raise ValueError("No airline code in '{}' ".format(number))

        if not number[:2].isupper():
            raise ValueError("Invalid airline code in '{}' ".format(number))

        if not (number[2:].isdigit() and int(number[2:]) <= 9999):
            raise ValueError("Invalid route number '{}' ".format(number))

        self._number = number
        self._aircraft = aircraft

        rows, seats = self._aircraft.seating_plan()
        # We start with None as lists are zero-indexed but the seating plan is one-indexed
        self._seating = [None] + [{letter: None for letter in seats} for _ in rows]

    def number(self):
        return self._number

    def airline(self):
        return self._number[:2]

    def aircraft_model(self):
        return self._aircraft.model()

    def allocate_seat(self, seat, passenger):
        """Allocates a seat to a passenger if the seat number is valid and not occupied.

        Args:
            seat: a seat designator eg '12A'.
            passenger: the passenger name.

        Raises:
            ValueError: if the seat is unavailable.
        """
        rows, seat_letters = self._aircraft.seating_plan()

        letter = seat[-1]
        if letter not in seat_letters:
            raise ValueError("Invalid seat letter '{}".format(letter))

        row_text = seat[:-1]
        try:
            row = int(row_text)
        except ValueError:
            raise ValueError("Invalid seat row '{}".format(row_text))

        if row not in rows:
            raise ValueError("Invalid row number '{}'".format(row))

        if self._seating[row][letter] is not None:
            raise ValueError("Seat {} is already occupied".format(seat))

        self._seating[row][letter] = passenger

    def available_routes(self, dept):
        return self._aircraft.available_routes(dept)

    def num_available_seats(self):
        return sum(sum(1 for s in row.values() if s is None)
                   for row in self._seating
                   if row is not None)

    def make_boarding_cards(self, card_printer):
        for passenger, seat in sorted(self._passenger_seats()):
            card_printer(passenger, seat, self.number(), self.aircraft_model())

    def _passenger_seats(self):
        """A generator for an iterable series of passenger seating allocations"""
        row_numbers, seat_letters = self._aircraft.seating_plan()
        for row in row_numbers:
            for letter in seat_letters:
                passenger = self._seating[row][letter]
                if passenger is not None:
                    yield (passenger, "{}{}".format(row, letter))


class Aircraft:
    """An aircraft with a given registration"""

    def __init__(self, registration):
        self._registration = registration

    def registration(self):
        return self._registration

    def num_seats(self):
        rows, row_seats = self.seating_plan()
        return len(rows) * len(row_seats)


class AirbusA319(Aircraft):

    def available_routes(self, dept):
        """Returns available destinations for this aircraft type from a departure location
        Args:
            dept: String representing departure airline code
        """
        # TODO take these routes from an API
        routes = {'EDB': ['LCY', 'LGW', 'LHR'],
                  'LCY': ['ABZ', 'GLA', 'EDB'],
                  'LGW': ['ABZ', 'EDB', 'GLA'],
                  'LHR': ['ABZ', 'EDB', 'GLA']}
        try:
            return routes.get(dept)

        except ValueError:
            raise ValueError("Departures from '{}' are not available on Airbus A319".format(dept))

    def model(self):
        return "Airbus A319"

    def seating_plan(self):
        return range(1, 23), "ABCDEF"


class Boeing777(Aircraft):

    def available_routes(self, dept):
        # TODO take these routes from an API
        routes = {'EDB': ['LHR'],
                  'LGW': ['BFS', 'EDB', 'GLA'],
                  'LHR': ['BFS', 'EDB', 'GLA']}
        try:
            return routes.get(dept)

        except ValueError:
            raise ValueError("Departures from '{}' are not available on Boeing 777".format(dept))

    def model(self):
        return "Boeing 777"

    def seating_plan(self):
        return range(1, 56), "ABCDEFGHJK"


def make_flights():
    """	Make Flight objects for testing instead of creating at the REPL
        Returns:
            Flight objects f,g
    """
    f = Flight("BA758", AirbusA319("G-EUPT"))
    f.allocate_seat('12A', 'Guido van Rossum')
    f.allocate_seat('12F', 'John Smith')
    f.allocate_seat('15C', 'Anders Hejlsberg')
    f.allocate_seat('1C', 'Paul McCarthy')
    f.allocate_seat('1F', 'Richard Hickey')

    g = Flight("AF72", Boeing777("F-GSPS"))
    g.allocate_seat('55K', 'Guido van Rossum')
    g.allocate_seat('33G', 'John Smith')
    g.allocate_seat('4B', 'Anders Hejlsberg')
    g.allocate_seat('4A', 'Paul McCarthy')

    return f, g


def console_card_printer(passenger, seat, flight_number, aircraft):
    """Creates and prints boarding passes for passengers in alphabetical order
    Args:
        passenger: the passenger name
        seat: the seat reference
        flight_number: the flight number for the passenger
        aircraft: the aircraft ID
    """
    output = "| Name: {0}"		\
             "  Flight: {1}"	\
             "  Seat: {2}" 		\
             "  Aircraft: {3}" 	\
             "  |".format(passenger, flight_number, seat, aircraft)

    banner = '+' + '-' * (len(output) - 2) + '+'
    border = '|' + ' ' * (len(output) - 2) + '|'
    lines = [banner, border, output, border, banner]
    card = '\n'.join(lines)
    print(card)
    print()
