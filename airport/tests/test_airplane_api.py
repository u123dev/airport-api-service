from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import  Airplane
from airport.serializers import AirplaneListSerializer, AirplaneSerializer
from airport.tests.init_sample import (
    init_sample_user,
    init_sample_superuser,
    init_sample_airplane,
    init_sample_airplane_type
)

AIRPLANE_URL = reverse("airport:airplane-list")
AIRPLANE_DETAIL = "airport:airplane-detail"


def detail_url(instance_id):
    return reverse(AIRPLANE_DETAIL, args=[instance_id])


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_airplane_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_user()
        self.client.force_authenticate(self.user)

    def test_list_airplanes(self):
        init_sample_airplane(name="Sample airplane1")
        init_sample_airplane(name="Sample airplane2")
        res = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.order_by("name")
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_city_detail(self):
        init_sample_airplane(name="Sample airplane1")
        airplane = init_sample_airplane(name="Sample airplane2")

        res = self.client.get(detail_url(airplane.id))

        serializer = AirplaneListSerializer(airplane)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_forbidden(self):
        payload = {"name": "Sample airplane to create", }
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_airplane_forbidden(self):
        airplane = init_sample_airplane()
        airplane.name = "Updated airplane"
        res = self.client.put(detail_url(airplane.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_airplane_forbidden(self):
        airplane = init_sample_airplane()
        res = self.client.delete(detail_url(airplane.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_superuser()
        self.client.force_authenticate(self.user)

    def test_list_airplanes(self):
        init_sample_airplane(name="Sample airplane1")
        init_sample_airplane(name="Sample airplane2")
        res = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.order_by("name")
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_airplane_detail(self):
        init_sample_airplane(name="Sample airplane1")
        airplane = init_sample_airplane(name="Sample airplane2")

        res = self.client.get(detail_url(airplane.id))

        serializer = AirplaneListSerializer(airplane)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane(self):
        airplane_type = init_sample_airplane_type(name="Sample airplane type1")
        payload = {
            "name": "Sample airplane to create",
            "rows": 77,
            "seats_in_row": 9,
            "airplane_type": airplane_type.id,
        }
        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.get(id=res.data["id"])
        serializer = AirplaneSerializer(airplane)
        for key in payload.keys():
            self.assertEqual(serializer.data.get(key), payload.get(key))

    def test_update_airplane(self):
        airplane = init_sample_airplane(name="Sample airplane")
        airplane_type2 = init_sample_airplane_type(name="Sample airplane type2")
        payload = {
            "id": airplane.id,
            "name": "Update airplane",
            "rows": 22,
            "seats_in_row": 11,
            "airplane_type": airplane_type2.id,
        }
        res = self.client.put(detail_url(airplane.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        airplane_updated = Airplane.objects.get(id=airplane.id)
        serializer = AirplaneSerializer(airplane_updated)
        for key, value in payload.items():
            self.assertEqual(serializer.data[key], value)

    def test_delete_airplane(self):
        airplane = init_sample_airplane()
        res = self.client.delete(detail_url(airplane.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
