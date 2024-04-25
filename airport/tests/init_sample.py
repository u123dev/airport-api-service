from datetime import datetime, timedelta

from django.contrib.auth import get_user_model

from airport.models import (
    Country,
    City,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket
)


def init_sample_user():
    return get_user_model().objects.create_user(
        "test@test.com",
        "testpass",
    )

def init_sample_superuser():
    return get_user_model().objects.create_superuser(
        "test@test.com",
        "testpass",
    )

def init_sample_country(**params):
    defaults = {"name": "Sample country", }
    defaults.update(params)
    return Country.objects.get_or_create(**defaults)[0]

def init_sample_city(**params):
    country1 = init_sample_country(name="Sample country 1")
    defaults = {"name": "Sample city1", "country": country1}
    defaults.update(params)
    return City.objects.get_or_create(**defaults)[0]

def init_sample_airport(**params):
    country1 = init_sample_country(name="Sample country 1")
    city1 = init_sample_city(name="Sample city 1", country=country1)
    defaults = {"name": "Sample airport1", "closest_big_city": city1}
    defaults.update(params)
    return Airport.objects.get_or_create(**defaults)[0]

def init_sample_route(**params):
    airport1 = init_sample_airport(name="Sample airport 1")
    airport2 = init_sample_airport(name="Sample airport 2")
    defaults = {"source": airport1, "destination": airport2, "distance": 99}
    defaults.update(params)
    return Route.objects.get_or_create(**defaults)[0]

def init_sample_airplane_type(**params):
    defaults = {"name": "Sample airplane type", }
    defaults.update(params)
    return AirplaneType.objects.get_or_create(**defaults)[0]

def init_sample_airplane(**params):
    airplane_type1 = init_sample_airplane_type(name="Sample airplane type 1")
    defaults = {"name": "Sample airplane", "airplane_type": airplane_type1, "rows": 10, "seats_in_row": 10}
    defaults.update(params)
    return Airplane.objects.get_or_create(**defaults)[0]

def init_sample_crew(**params):
    defaults = {"first_name": "First1", "last_name": "Last1"}
    defaults.update(params)
    return Crew.objects.get_or_create(**defaults)[0]

def init_sample_flight(**params):
    route = init_sample_route()
    airplane = init_sample_airplane()
    crew1 = init_sample_crew()
    crew2 = init_sample_crew(first_name="First2", last_name="Last2")
    departure_time = datetime.now()
    arrival_time = datetime.now() + timedelta(days=11)

    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": departure_time,
        "arrival_time": arrival_time
    }
    defaults.update(params)
    flight = Flight.objects.get_or_create(**defaults)[0]
    flight.crew.add(crew1, crew2)
    flight.save()
    return flight

def init_sample_order(**params):
    flight = init_sample_flight()
    tickets_data = [
        {"row": 1, "seat": 1, "flight": flight},
        {"row": 2, "seat": 2, "flight": flight},
    ]

    defaults = {
        "user": None,
        "created_at": datetime.now(),
    }
    defaults.update(params)
    order = Order.objects.get_or_create(**defaults)[0]
    for ticket_data in tickets_data:
        Ticket.objects.create(order=order, **ticket_data)
    return order
