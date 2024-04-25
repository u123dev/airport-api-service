from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Order
from airport.serializers import OrderListSerializer, OrderSerializer
from airport.tests.init_sample import init_sample_user, init_sample_superuser, init_sample_flight, init_sample_order

ORDER_URL = reverse("airport:order-list")
ORDER_DETAIL = "airport:order-detail"


def detail_url(instance_id):
    return reverse(ORDER_DETAIL, args=[instance_id])


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_flight_auth_required(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_user()
        self.client.force_authenticate(self.user)

    def test_list_orders(self):
        init_sample_order(user=self.user)
        init_sample_order(user=self.user)
        res = self.client.get(ORDER_URL)

        orders = Order.objects.order_by("-created_at")
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key, value in serializer.data[0].items():
            self.assertEqual(res.data["results"][0][key], value)

    def test_retrieve_order_detail(self):
        init_sample_order(user=self.user)
        order = init_sample_order(user=self.user)
        res = self.client.get(detail_url(order.id))

        serializer = OrderSerializer(order)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_order_forbidden(self):
        res = self.client.post(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_superuser()
        self.client.force_authenticate(self.user)

    def test_create_order(self):
        flight = init_sample_flight()
        tickets_data = {
            "tickets": [
                {"row": 1, "seat": 1, "flight": flight.id},
                {"row": 2, "seat": 2, "flight": flight.id},
            ]
        }
        res = self.client.post(ORDER_URL, tickets_data, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=res.data["id"])
        serializer = OrderSerializer(order)

        self.assertEqual(res.data, serializer.data)

###############
    def test_update_order(self):
        order = init_sample_order(user=self.user)
        res = self.client.put(detail_url(order.id))
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_order(self):
        order = init_sample_order(user=self.user)
        res = self.client.delete(detail_url(order.id))
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
