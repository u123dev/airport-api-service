from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Crew
from airport.serializers import CrewSerializer
from airport.tests.init_sample import init_sample_user, init_sample_superuser, init_sample_crew

CREW_URL = reverse("airport:crew-list")
CREW_DETAIL = "airport:crew-detail"


def detail_url(instance_id):
    return reverse(CREW_DETAIL, args=[instance_id])


class UnauthenticatedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_crew_auth_required(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_user()
        self.client.force_authenticate(self.user)

    def test_list_crews(self):
        init_sample_crew()
        init_sample_crew(first_name="First2", last_name="Last2")
        res = self.client.get(CREW_URL)

        crews = Crew.objects.order_by("last_name")
        serializer = CrewSerializer(crews, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_crew_detail(self):
        init_sample_crew()
        crew = init_sample_crew(first_name="First2", last_name="Last2")
        res = self.client.get(detail_url(crew.id))

        serializer = CrewSerializer(crew)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_crew_forbidden(self):
        payload = {"first_name": "Sample First", "last_name": "Sample Last",}
        res = self.client.post(CREW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_crew_forbidden(self):
        crew = init_sample_crew()
        crew.first_name = "Updated First"
        res = self.client.put(detail_url(crew.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_crew_forbidden(self):
        crew = init_sample_crew()
        res = self.client.delete(detail_url(crew.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_superuser()
        self.client.force_authenticate(self.user)

    def test_list_crews(self):
        init_sample_crew()
        init_sample_crew(first_name="First2", last_name="Last2")
        res = self.client.get(CREW_URL)

        crews = Crew.objects.order_by("last_name")
        serializer = CrewSerializer(crews, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_crew_detail(self):
        init_sample_crew()
        crew = init_sample_crew(first_name="First2", last_name="Last2")
        res = self.client.get(detail_url(crew.id))

        serializer = CrewSerializer(crew)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_crew(self):
        payload = {"first_name": "Sample First", "last_name": "Sample Last",}
        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        crew = Crew.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(crew, key))

    def test_update_crew(self):
        crew = init_sample_crew()
        payload = {"id": crew.id, "first_name": "Updated First", "last_name": "Updated Last" }
        res = self.client.put(detail_url(crew.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_crew(self):
        crew = init_sample_crew()
        res = self.client.delete(detail_url(crew.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
