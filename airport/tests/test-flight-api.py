from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Flight
from airport.serializers import FlightSerializer, FlightListSerializer, FlightDetailSerializer
from airport.tests.init_sample import (
    init_sample_user,
    init_sample_superuser,
    init_sample_crew,
    init_sample_flight,
    init_sample_route,
    init_sample_airplane, init_sample_airport
)

FLIGHT_URL = reverse("airport:flight-list")
FLIGHT_DETAIL = "airport:flight-detail"


def detail_url(instance_id):
    return reverse(FLIGHT_DETAIL, args=[instance_id])


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_flight_auth_required(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_user()
        self.client.force_authenticate(self.user)

    def test_list_flights(self):
        init_sample_flight()
        init_sample_flight()
        res = self.client.get(FLIGHT_URL)

        flights = Flight.objects.order_by("departure_time")
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key, value in serializer.data[0].items():
            self.assertEqual(res.data[0][key], value)

    def test_filter_flights_by_source(self):
        route1 = init_sample_route(
            source=init_sample_airport(name="Aport1"),
            destination=init_sample_airport(name="Aport2")
        )
        route2 = init_sample_route(
            source=init_sample_airport(name="Aport1 smth"),
            destination=init_sample_airport(name="Aport3")
        )
        route3 = init_sample_route(
            source=init_sample_airport(name="Aport4"),
            destination=init_sample_airport(name="Aport2 other")
        )
        flight1 = init_sample_flight(route=route1)
        flight2 = init_sample_flight(route=route2)
        flight3 = init_sample_flight(route=route3)
        res = self.client.get(FLIGHT_URL, {"source": "aport1"})

        flights = (
            Flight.objects.
            filter(route__source__name__icontains="aport1").
            order_by("departure_time")
        )
        serializer1 = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key, value in serializer1.data[0].items():
            self.assertEqual(res.data[0][key], value)

    def test_filter_flights_by_destination(self):
        route1 = init_sample_route(
            source=init_sample_airport(name="Aport1"),
            destination=init_sample_airport(name="Aport2")
        )
        route2 = init_sample_route(
            source=init_sample_airport(name="Aport1 smth"),
            destination=init_sample_airport(name="Aport3")
        )
        route3 = init_sample_route(
            source=init_sample_airport(name="Aport4"),
            destination=init_sample_airport(name="Aport2 other")
        )
        flight1 = init_sample_flight(route=route1)
        flight2 = init_sample_flight(route=route2)
        flight3 = init_sample_flight(route=route3)
        res = self.client.get(FLIGHT_URL, {"destination": "aport2"})

        flights = (
            Flight.objects.
            filter(route__destination__name__icontains="aport2").
            order_by("departure_time")
        )
        serializer1 = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key, value in serializer1.data[0].items():
            self.assertEqual(res.data[0][key], value)

    def test_filter_flights_by_departure_date_after(self):
        departure_date_after = datetime.now()
        route1 = init_sample_route()
        route2 = init_sample_route()
        route3 = init_sample_route()
        flight1 = init_sample_flight(route=route1, departure_time=departure_date_after - timedelta(days=2))
        flight2 = init_sample_flight(route=route2, departure_time=departure_date_after)
        flight3 = init_sample_flight(route=route3, departure_time=departure_date_after + timedelta(days=10))
        res = self.client.get(FLIGHT_URL, {"departure_date_after": departure_date_after.date()})

        flights = (
            Flight.objects.
            filter(departure_time__date__gte=departure_date_after.date()).
            order_by("departure_time")
        )
        serializer1 = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key, value in serializer1.data[0].items():
            self.assertEqual(res.data[0][key], value)

    def test_filter_flights_by_departure_date_before(self):
        departure_date_before = datetime.now() + timedelta(days=2)
        route1 = init_sample_route()
        route2 = init_sample_route()
        route3 = init_sample_route()
        flight1 = init_sample_flight(route=route1, departure_time=departure_date_before - timedelta(days=1))
        flight2 = init_sample_flight(route=route2, departure_time=departure_date_before)
        flight3 = init_sample_flight(route=route3, departure_time=departure_date_before + timedelta(days=3))
        res = self.client.get(FLIGHT_URL, {"departure_date_after": departure_date_before.date()})

        flights = (
            Flight.objects.
            filter(departure_time__date__gte=departure_date_before.date()).
            order_by("departure_time")
        )
        serializer1 = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key, value in serializer1.data[0].items():
            self.assertEqual(res.data[0][key], value)

    def test_filter_flights_by_arrival_date_after(self):
        arrival_date_after = datetime.now() + timedelta(days=3)
        route1 = init_sample_route()
        route2 = init_sample_route()
        route3 = init_sample_route()
        flight1 = init_sample_flight(route=route1, arrival_time=arrival_date_after - timedelta(days=2))
        flight2 = init_sample_flight(route=route2, arrival_time=arrival_date_after)
        flight3 = init_sample_flight(route=route3, arrival_time=arrival_date_after + timedelta(days=5))
        res = self.client.get(FLIGHT_URL, {"arrival_date_after": arrival_date_after.date()})

        flights = (
            Flight.objects.
            filter(arrival_time__date__gte=arrival_date_after.date()).
            order_by("departure_time")
        )
        serializer1 = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key, value in serializer1.data[0].items():
            self.assertEqual(res.data[0][key], value)

    def test_filter_flights_by_arrival_date_before(self):
        arrival_date_before = datetime.now() + timedelta(days=2)
        route1 = init_sample_route()
        route2 = init_sample_route()
        route3 = init_sample_route()
        flight1 = init_sample_flight(route=route1, departure_time=arrival_date_before - timedelta(days=1))
        flight2 = init_sample_flight(route=route2, departure_time=arrival_date_before)
        flight3 = init_sample_flight(route=route3, departure_time=arrival_date_before + timedelta(days=3))
        res = self.client.get(FLIGHT_URL, {"arrival_date_after": arrival_date_before.date()})

        flights = (
            Flight.objects.
            filter(arrival_time__date__gte=arrival_date_before.date()).
            order_by("departure_time")
        )
        serializer1 = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key, value in serializer1.data[0].items():
            self.assertEqual(res.data[0][key], value)

    def test_retrieve_flight_detail(self):
        init_sample_flight()
        flight = init_sample_flight()
        res = self.client.get(detail_url(flight.id))

        serializer = FlightDetailSerializer(flight)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_flight_forbidden(self):
        res = self.client.post(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_flight_forbidden(self):
        flight = init_sample_flight()
        res = self.client.put(detail_url(flight.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_flight_forbidden(self):
        flight = init_sample_flight()
        res = self.client.delete(detail_url(flight.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_superuser()
        self.client.force_authenticate(self.user)

    def test_list_flights(self):
        init_sample_flight()
        init_sample_flight()
        res = self.client.get(FLIGHT_URL)

        flights = Flight.objects.order_by("departure_time")
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key, value in serializer.data[0].items():
            self.assertEqual(res.data[0][key], value)

    def test_retrieve_flight_detail(self):
        init_sample_flight()
        flight = init_sample_flight()
        res = self.client.get(detail_url(flight.id))

        serializer = FlightDetailSerializer(flight)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_flight(self):
        route = init_sample_route()
        airplane = init_sample_airplane()
        crew1 = init_sample_crew()
        crew2 = init_sample_crew(first_name="First2", last_name="Last2")
        departure_time = datetime(2024, 4, 27, 10, 11)
        arrival_time = datetime(2024, 4, 28, 9 , 9)

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "crew": [crew1.id, crew2.id],
            "departure_time": departure_time,
            "arrival_time": arrival_time
        }
        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        flight = Flight.objects.get(id=res.data["id"])
        serializer = FlightSerializer(flight)

        self.assertEqual(res.data, serializer.data)

    def test_update_flight(self):
        flight = init_sample_flight()
        res = self.client.put(detail_url(flight.id))
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_flight(self):
        flight = init_sample_flight()
        res = self.client.delete(detail_url(flight.id))
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
