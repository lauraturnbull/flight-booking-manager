"""Model for flight booking management system"""


class Flight:
    """A flight with a particular passenger aircraft."""

    def __init__(self, number, dept, dest, aircraft):
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
        self._dept = dept
        self._dest = dest

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

    def available_routes(self):
        return self._aircraft.available_routes()

    def flight_route(self):
        return self._aircraft.flight_route(self._dept, self._dest)

    def num_available_seats(self):
        return sum(sum(1 for s in row.values() if s is None)
                   for row in self._seating
                   if row is not None)

    def make_boarding_cards(self, card_printer):
        for passenger, seat in sorted(self._passenger_seats()):
            card_printer(passenger, seat, self._dept, self._dest, self.number(), self.aircraft_model())

    def _passenger_seats(self):
        """A generator for an iterable series of passenger seating allocations"""
        row_numbers, seat_letters = self._aircraft.seating_plan()
        for row in row_numbers:
            for letter in seat_letters:
                passenger = self._seating[row][letter]
                if passenger is not None:
                    yield (passenger, "{}{}".format(row, letter))

    def _seat_generator(self):
        row_numbers, seat_letters = self._aircraft.seating_plan()
        for row in row_numbers:
            for letter in seat_letters:
                passenger = self._seating[row][letter]
                if passenger is None:
                    yield ("{}{}".format(row, letter))


class Aircraft:
    """An aircraft with a given registration"""

    def __init__(self, registration):
        self._registration = registration

    def registration(self):
        return self._registration

    def num_seats(self):
        rows, row_seats = self.seating_plan()
        return len(rows) * len(row_seats)

    def available_routes(self):
        return self.avail_routes()

    def flight_route(self, dept, dest):
        """Returns the route for this flight object
        Args:
            dept: String representing departure airport code
            dest: String representing destination airport code

        Returns:
              Tuple of (dept, dest) if available
              -1 if the route is not available
        """
        routes = self.available_routes()

        if routes.get(dept) and dest in routes.get(dept):
            return dept, dest
        else:
            return -1


class AirbusA319(Aircraft):

    def avail_routes(self):
        # TODO take these routes from an API
        routes = {'EDB': ['LCY', 'LGW', 'LHR'],
                  'LCY': ['ABZ', 'GLA', 'EDB'],
                  'LGW': ['ABZ', 'EDB', 'GLA'],
                  'LHR': ['ABZ', 'EDB', 'GLA']}
        return routes

    def model(self):
        return "Airbus A319"

    def seating_plan(self):
        return range(1, 23), "ABCDEF"


class Boeing777(Aircraft):

    def avail_routes(self):
        # TODO take these routes from an API
        routes = {'EDB': ['LHR'],
                  'LGW': ['BFS', 'EDB', 'GLA'],
                  'LHR': ['BFS', 'EDB', 'GLA']}
        return routes

    def model(self):
        return "Boeing 777"

    def seating_plan(self):
        return range(1, 56), "ABCDEFGHJK"


def create_flight():
    """Creates Flight objects for new flights and assigns the next available seat to the passenger.
        If a Flight object with a given flight number already exists the Passenger is added to this flight.
        Reads:
            A text file with booking information in the order(comma-separated):
            NAME,DEPARTURE CODE,DESTINATION CODE,FLIGHT NUMBER,AIRCRAFT TYPE,REGISTRATION
        Returns:
            A list of flight objects with passengers assigned to seats.
            Warnings printed to REPL if invalid routes are input or if the route does not match the
            existing flight's.
    """
    flight_objects = []
    with open('Passengers.txt', 'r') as data:
        bookings =[line.split(',') for line in data]

    for item in bookings:
        _name, _dept, _dest, _number, _aircraft, _reg = item[0], item[1], item[2], item[3], item[4], item[5]
        existing_flights = [x[1] for x in flight_objects]

        if _number not in existing_flights and _aircraft == "AirbusA319":
            test_craft = AirbusA319(_reg)
            if test_craft.flight_route(_dept, _dest)!= -1:

                flightobj = Flight(_number, _dept, _dest, AirbusA319(_reg))
                _seat = (flightobj._seat_generator().__next__())
                flightobj.allocate_seat(_seat, _name)
                flight_objects.append((flightobj, _number))
            else:
                print("Passenger {} not added to flight {}. There are no {} flights from {}-{}."
                      .format( _name, _number, _aircraft, _dept, _dest))

        elif _number not in existing_flights and _aircraft == "Boeing777":
            test_craft = AirbusA319(_reg)
            if test_craft.flight_route(_dept, _dest)!= -1:

                flightobj = Flight(_number, _dept, _dest, Boeing777(_reg))
                _seat = (flightobj._seat_generator().__next__())
                flightobj.allocate_seat(_seat, _name)
                flight_objects.append((flightobj, _number))

        else:
            flightindex = existing_flights.index(_number)
            flightobj = flight_objects[flightindex][0]
            if flightobj.flight_route() == (_dept, _dest):

                _seat = (flightobj._seat_generator().__next__())
                flightobj.allocate_seat(_seat, _name)
            else:
                print("Passenger {} not added to flight {} as incorrect DEPT or DEST codes input. "
                      "This flight has route {}-{}.".format( _name, _number, _dept, _dest))

    return [i[0] for i in flight_objects]


def console_card_printer(passenger, seat, dept, dest, flight_number, aircraft):
    """Creates and prints boarding passes for passengers in alphabetical order
    Args:
        passenger: the passenger name
        seat: the seat reference
        flight_number: the flight number for the passenger
        aircraft: the aircraft ID
    """
    output = "| Name: {0}"		\
             "  Flight: {1}, {2}-{3}"	\
             "  Seat: {4}" 		\
             "  Aircraft: {5}" 	\
             "  |".format(passenger, flight_number, dept, dest, seat, aircraft)

    banner = '+' + '-' * (len(output) - 2) + '+'
    border = '|' + ' ' * (len(output) - 2) + '|'
    lines = [banner, border, output, border, banner]
    card = '\n'.join(lines)
    print(card)
    print()
