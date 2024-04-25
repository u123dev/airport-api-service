import os
import tempfile

from PIL import Image
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Crew
from airport.tests.init_sample import init_sample_superuser, init_sample_crew, init_sample_flight

CREW_URL = reverse("airport:crew-list")
CREW_DETAIL = "airport:crew-detail"
CREW_PHOTO = "airport:crew-upload"
FLIGHT_URL = reverse("airport:flight-list")
FLIGHT_DETAIL = "airport:flight-detail"


def detail_url(instance_id):
    return reverse(CREW_DETAIL, args=[instance_id])


def detail_flight_url(instance_id):
    return reverse(FLIGHT_DETAIL, args=[instance_id])


def image_upload_url(instance_id):
    """Return URL for recipe image upload"""
    return reverse(CREW_PHOTO, args=[instance_id])


class CrewPhotoUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_superuser()
        self.client.force_authenticate(self.user)
        self.crew = init_sample_crew()
        self.flight = init_sample_flight()
        self.flight.crew.add(self.crew)
        self.flight.save()

    def tearDown(self):
        self.crew.photo.delete()

    def test_upload_photo_to_crew(self):
        """Test uploading photo to crew"""
        url = image_upload_url(self.crew.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"photo": ntf}, format="multipart")
        self.crew.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("photo", res.data)
        self.assertTrue(os.path.exists(self.crew.photo.path))

    def test_upload_photo_bad_request(self):
        """Test uploading an invalid photo"""
        url = image_upload_url(self.crew.id)
        res = self.client.post(url, {"photo": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_photo_to_crew_list_should_not_work(self):
        url = CREW_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "first_name": "first_name",
                    "last_name": "last_name",
                    "photo": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        crew = Crew.objects.get(first_name="first_name")
        self.assertFalse(crew.photo)

    def test_photo_url_is_shown_on_crew_detail(self):
        url = image_upload_url(self.crew.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"photo": ntf}, format="multipart")
        res = self.client.get(detail_url(self.crew.id))

        self.assertIn("photo", res.data)

    def test_photo_url_is_shown_on_crew_list(self):
        url = image_upload_url(self.crew.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"photo": ntf}, format="multipart")
        res = self.client.get(CREW_URL)

        self.assertIn("photo", res.data[0].keys())

    def test_photo_url_is_shown_on_flight_detail(self):
        url = image_upload_url(self.crew.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"photo": ntf}, format="multipart")
        res = self.client.get(detail_flight_url(self.flight.id))

        self.assertIn("photo", res.data.get("crew")[0].keys())
