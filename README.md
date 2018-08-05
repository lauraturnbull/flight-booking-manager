# flight-booking-manager
Creates Flight and Aircraft objects. 
Assigns Passengers to seating plan based on Aircraft type. 
Can print boarding passes to REPL for flights.

To create Flight objects run 
"f, g = make_flights()"

To create boarding cards for flight objects run
"f.make_boarding_cards(console_card_printer)"
at the REPL

To create Aircraft objects run (for example)
"a = Airbus("G-EZBT")" where the arg is the aircraft registration
