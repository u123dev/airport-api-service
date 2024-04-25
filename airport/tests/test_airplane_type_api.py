from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import AirplaneType
from airport.serializers import AirplaneTypeSerializer
from airport.tests.init_sample import init_sample_user, init_sample_superuser, init_sample_airplane_type

AIRPLANE_TYPE_URL = reverse("airport:airplanetype-list")
AIRPLANE_TYPE_DETAIL = "airport:airplanetype-detail"


def detail_url(instance_id):
    return reverse(AIRPLANE_TYPE_DETAIL, args=[instance_id])


class UnauthenticatedAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_country_auth_required(self):
        res = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_user()
        self.client.force_authenticate(self.user)

    def test_list_airplane_types(self):
        init_sample_airplane_type(name="Sample airplane_type1")
        init_sample_airplane_type(name="Sample airplane_type2")
        res = self.client.get(AIRPLANE_TYPE_URL)

        airplane_types = AirplaneType.objects.order_by("name")
        serializer = AirplaneTypeSerializer(airplane_types, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_country_detail(self):
        init_sample_airplane_type(name="Sample airplane_type1")
        airplane_type = init_sample_airplane_type(name="Sample airplane_type2")

        res = self.client.get(detail_url(airplane_type.id))

        serializer = AirplaneTypeSerializer(airplane_type)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_type_forbidden(self):
        payload = {"name": "Sample airplane type to create", }
        res = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_airplane_type_forbidden(self):
        airplane_type = init_sample_airplane_type(name="Sample airplane_type")
        airplane_type.name = "Updated airplane_type"
        res = self.client.put(detail_url(airplane_type.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_airplane_type_forbidden(self):
        airplane_type = init_sample_airplane_type(name="Sample airplane_type")
        res = self.client.delete(detail_url(airplane_type.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_superuser()
        self.client.force_authenticate(self.user)

    def test_list_airplane_type(self):
        init_sample_airplane_type(name="Sample airplane_type1")
        init_sample_airplane_type(name="Sample airplane_type2")
        res = self.client.get(AIRPLANE_TYPE_URL)

        airplane_types = AirplaneType.objects.order_by("name")
        serializer = AirplaneTypeSerializer(airplane_types, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_airplane_type_detail(self):
        init_sample_airplane_type()
        airplane_type = init_sample_airplane_type()

        res = self.client.get(detail_url(airplane_type.id))

        serializer = AirplaneTypeSerializer(airplane_type)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_type(self):
        payload = {"name": "Sample airplane_type to create", }
        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane_type = AirplaneType.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(airplane_type, key))

    def test_update_airplane_type(self):
        airplane_type = init_sample_airplane_type(name="Sample airplane_type")
        payload = {"id": airplane_type.id, "name": "Updated Sample airplane_type", }
        res = self.client.put(detail_url(airplane_type.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_airplane_type(self):
        airplane_type = init_sample_airplane_type(name="Sample airplane_type")
        res = self.client.delete(detail_url(airplane_type.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
