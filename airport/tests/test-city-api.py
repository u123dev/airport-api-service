from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import City
from airport.serializers import CityListSerializer, CitySerializer
from airport.tests.init_sample import (
    init_sample_user,
    init_sample_country,
    init_sample_superuser,
    init_sample_city
)

CITY_URL = reverse("airport:city-list")
CITY_DETAIL = "airport:city-detail"


def detail_url(instance_id):
    return reverse(CITY_DETAIL, args=[instance_id])


class UnauthenticatedCityApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_city_auth_required(self):
        res = self.client.get(CITY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCityApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_user()
        self.client.force_authenticate(self.user)

    def test_list_cities(self):
        init_sample_city(name="Sample city1")
        init_sample_city(name="Sample city2")
        res = self.client.get(CITY_URL)

        cities = City.objects.order_by("name")
        serializer = CityListSerializer(cities, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_city_detail(self):
        init_sample_city(name="Sample city1")
        city = init_sample_city(name="Sample city2")

        res = self.client.get(detail_url(city.id))

        serializer = CityListSerializer(city)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_city_forbidden(self):
        payload = {"name": "Sample city to create", }
        res = self.client.post(CITY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_city_forbidden(self):
        city = init_sample_country(name="Sample city")
        city.name = "Updated city"
        res = self.client.put(detail_url(city.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_city_forbidden(self):
        city = init_sample_city(name="Sample city")
        res = self.client.delete(detail_url(city.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCiiyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_superuser()
        self.client.force_authenticate(self.user)

    def test_list_cities(self):
        init_sample_city(name="Sample city1")
        init_sample_city(name="Sample city2")
        res = self.client.get(CITY_URL)

        cities = City.objects.order_by("name")
        serializer = CityListSerializer(cities, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_city_detail(self):
        init_sample_city(name="Sample city1")
        city = init_sample_city(name="Sample city2")

        res = self.client.get(detail_url(city.id))

        serializer = CityListSerializer(city)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_city(self):
        country = init_sample_country(name="Sample country1")
        payload = {"name": "Sample city to create", "country": country.id, }
        res = self.client.post(CITY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        city = City.objects.get(id=res.data["id"])
        serializer = CitySerializer(city)
        for key in payload.keys():
            self.assertEqual(serializer.data.get(key), payload.get(key))


    def test_update_city(self):
        country = init_sample_country(name="Sample country")
        city = init_sample_city(name="Sample city", country=country)
        payload = {"id": city.id, "name": "Updated Sample city", "country": country.id, }
        res = self.client.put(detail_url(city.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        city_updated = City.objects.get(id=city.id)
        serializer = CitySerializer(city_updated)
        self.assertEqual(serializer.data, payload)

    def test_delete_city(self):
        country = init_sample_country(name="Sample country")
        city = init_sample_city(name="Sample city", country=country)
        res = self.client.delete(detail_url(city.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
