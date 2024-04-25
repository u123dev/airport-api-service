import os
import tempfile

from PIL import Image
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airplane
from airport.tests.init_sample import (
    init_sample_superuser,
    init_sample_flight,
    init_sample_airplane,
    init_sample_airplane_type
)

AIRPLANE_URL = reverse("airport:airplane-list")
AIRPLANE_DETAIL = "airport:airplane-detail"
AIRPLANE_IMAGE = "airport:airplane-upload"
FLIGHT_URL = reverse("airport:flight-list")
FLIGHT_DETAIL = "airport:flight-detail"


def detail_url(instance_id):
    return reverse(AIRPLANE_DETAIL, args=[instance_id])


def detail_flight_url(instance_id):
    return reverse(FLIGHT_DETAIL, args=[instance_id])


def image_upload_url(instance_id):
    """Return URL for recipe image upload"""
    return reverse(AIRPLANE_IMAGE, args=[instance_id])


class AirplaneImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_superuser()
        self.client.force_authenticate(self.user)
        self.airplane = init_sample_airplane()
        self.flight = init_sample_flight()

    def tearDown(self):
        self.airplane.airplane_photo.delete()

    def test_upload_image_to_airplane(self):
        """Test uploading photo to airplane"""
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"airplane_photo": ntf}, format="multipart")
        self.airplane.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("airplane_photo", res.data)
        self.assertTrue(os.path.exists(self.airplane.airplane_photo.path))

    def test_upload_photo_bad_request(self):
        """Test uploading an invalid photo"""
        url = image_upload_url(self.airplane.id)
        res = self.client.post(url, {"airplane_photo": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_photo_to_airplane_list_should_not_work(self):
        url = AIRPLANE_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "air_name",
                    "rows": 10,
                    "seats_in_row": 10,
                    "airplane_type": init_sample_airplane_type().id,
                    "airplane_photo": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.get(name="air_name")
        self.assertFalse(airplane.airplane_photo)

    def test_photo_url_is_shown_on_airplane_detail(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"airplane_photo": ntf}, format="multipart")
        res = self.client.get(detail_url(self.airplane.id))

        self.assertIn("airplane_photo", res.data)

    def test_photo_url_is_shown_on_airplane_list(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"airplane_photo": ntf}, format="multipart")
        res = self.client.get(AIRPLANE_URL)

        self.assertIn("airplane_photo", res.data[0].keys())

    def test_photo_url_is_shown_on_flight_detail(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"airplane_photo": ntf}, format="multipart")
        res = self.client.get(detail_flight_url(self.flight.id))

        self.assertIn("airplane_photo", res.data.get("airplane").keys())
