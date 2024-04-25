from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport
from airport.serializers import AirportListSerializer, AirportSerializer
from airport.tests.init_sample import (
    init_sample_user,
    init_sample_country,
    init_sample_superuser,
    init_sample_city,
    init_sample_airport
)

AIRPORT_URL = reverse("airport:airport-list")
AIRPORT_DETAIL = "airport:airport-detail"


def detail_url(instance_id):
    return reverse(AIRPORT_DETAIL, args=[instance_id])


class UnauthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_city_auth_required(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_user()
        self.client.force_authenticate(self.user)

    def test_list_airports(self):
        init_sample_airport(name="Sample airport")
        init_sample_airport(name="Sample airport2")
        res = self.client.get(AIRPORT_URL)

        airports = Airport.objects.order_by("closest_big_city", "name")
        serializer = AirportListSerializer(airports, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_airport_detail(self):
        init_sample_airport(name="Sample airport")
        airport = init_sample_airport(name="Sample airport2")

        res = self.client.get(detail_url(airport.id))

        serializer = AirportListSerializer(airport)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airport_forbidden(self):
        payload = {"name": "Sample airport to create", }
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_airport_forbidden(self):
        airport = init_sample_country(name="Sample airport")
        airport.name = "Updated city"
        res = self.client.put(detail_url(airport.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_airport_forbidden(self):
        airport = init_sample_city(name="Sample airport")
        res = self.client.delete(detail_url(airport.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_superuser()
        self.client.force_authenticate(self.user)

    def test_list_airports(self):
        init_sample_airport(name="Sample airport")
        init_sample_airport(name="Sample airport2")
        res = self.client.get(AIRPORT_URL)

        airports = Airport.objects.order_by("closest_big_city", "name")
        serializer = AirportListSerializer(airports, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_airport_detail(self):
        init_sample_airport(name="Sample airport")
        airport = init_sample_airport(name="Sample airport2")

        res = self.client.get(detail_url(airport.id))

        serializer = AirportListSerializer(airport)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airport(self):
        city = init_sample_city(name="Sample city2")
        payload = {"name": "Sample city to create", "closest_big_city": city.id, }
        res = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airport = Airport.objects.get(id=res.data["id"])
        serializer = AirportSerializer(airport)
        for key in payload.keys():
            self.assertEqual(serializer.data.get(key), payload.get(key))


    def test_update_airport(self):
        city = init_sample_city(name="Sample city")
        airport = init_sample_airport(name="Sample airport")
        payload = {"id": airport.id, "name": "Updated airport", "closest_big_city": city.id, }
        res = self.client.put(detail_url(airport.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        airport_updated = Airport.objects.get(id=airport.id)
        serializer = AirportSerializer(airport_updated)
        self.assertEqual(serializer.data, payload)

    def test_delete_airport(self):
        airport = init_sample_airport(name="Sample airport")
        res = self.client.delete(detail_url(airport.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
