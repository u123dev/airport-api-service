from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Country
from airport.serializers import CountrySerializer
from airport.tests.init_sample import init_sample_user, init_sample_country, init_sample_superuser

COUNTRY_URL = reverse("airport:country-list")
COUNTRY_DETAIL = "airport:country-detail"


def detail_url(instance_id):
    return reverse(COUNTRY_DETAIL, args=[instance_id])


class UnauthenticatedCountryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_country_auth_required(self):
        res = self.client.get(COUNTRY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCountryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_user()
        self.client.force_authenticate(self.user)

    def test_list_countries(self):
        init_sample_country(name="Sample country1")
        init_sample_country(name="Sample country2")

        res = self.client.get(COUNTRY_URL)

        countries = Country.objects.order_by("name")
        serializer = CountrySerializer(countries, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_country_detail(self):
        init_sample_country(name="Sample country1")
        country = init_sample_country(name="Sample country2")

        res = self.client.get(detail_url(country.id))

        serializer = CountrySerializer(country)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_country_forbidden(self):
        payload = {"name": "Sample country to create", }
        res = self.client.post(COUNTRY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_country_forbidden(self):
        country = init_sample_country(name="Sample country")
        country.name = "Updated country"
        res = self.client.put(detail_url(country.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_country_forbidden(self):
        country = init_sample_country(name="Sample country")
        res = self.client.delete(detail_url(country.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCountryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_superuser()
        self.client.force_authenticate(self.user)

    def test_list_countries(self):
        init_sample_country(name="Sample country1")
        init_sample_country(name="Sample country2")

        res = self.client.get(COUNTRY_URL)

        countries = Country.objects.order_by("name")
        serializer = CountrySerializer(countries, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_country_detail(self):
        init_sample_country(name="Sample country1")
        country = init_sample_country(name="Sample country2")

        res = self.client.get(detail_url(country.id))

        serializer = CountrySerializer(country)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_country(self):
        payload = {"name": "Sample country to create", }
        res = self.client.post(COUNTRY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        country = Country.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(country, key))

    def test_update_country(self):
        country = init_sample_country(name="Sample country")
        payload = {"id": country.id, "name": "Updated Sample country", }
        res = self.client.put(detail_url(country.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_country(self):
        country = init_sample_country(name="Sample country")
        res = self.client.delete(detail_url(country.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
