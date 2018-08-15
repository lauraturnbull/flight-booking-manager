# flight-booking-manager
Creates Flight and Aircraft objects. 
Assigns Passengers to seating plan based on Aircraft type. 
Can print boarding passes to REPL for flights.


In the Python Console run "from mthree_1.py import *"

"x = create flight()" Will create flight objects and assign seats to the passengers in Passengers.txt


The flight objects are returned as a list. The first element in each tuple is the Flight object.
Boarding cards and other information can be found using 
"x[0].make_boarding_cards(console_card_printer)" etc.
