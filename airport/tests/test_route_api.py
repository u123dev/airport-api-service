from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Route
from airport.serializers import RouteListSerializer, RouteDetailSerializer, RouteSerializer
from airport.tests.init_sample import (
    init_sample_user,
    init_sample_superuser,
    init_sample_airport,
    init_sample_route
)

ROUTE_URL = reverse("airport:route-list")
ROUTE_DETAIL = "airport:route-detail"


def detail_url(instance_id):
    return reverse(ROUTE_DETAIL, args=[instance_id])


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_route_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_user()
        self.client.force_authenticate(self.user)

    def test_list_routes(self):
        init_sample_route()
        init_sample_route()
        res = self.client.get(ROUTE_URL)

        routes = Route.objects.order_by("source", "destination")
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_routes_by_source(self):
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
        res = self.client.get(ROUTE_URL, {"source": "aport1"})

        routes = (
            Route.objects.
            filter(source__name__icontains="aport1").
            order_by("source", "destination")
        )
        serializer1 = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer1.data)

    def test_filter_routes_by_destination(self):
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
        res = self.client.get(ROUTE_URL, {"destination": "aport2"})

        routes = (
            Route.objects.
            filter(destination__name__icontains="aport2").
            order_by("source", "destination")
        )
        serializer1 = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer1.data)

    def test_retrieve_route_detail(self):
        init_sample_route()
        route = init_sample_route()
        res = self.client.get(detail_url(route.id))

        serializer = RouteDetailSerializer(route)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        airport1 = init_sample_airport()
        airport2 = init_sample_airport()
        payload = {"source": airport1, "destination": airport2, "distance": 999 }
        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_route_forbidden(self):
        route = init_sample_route()
        route.distance = 888
        res = self.client.put(detail_url(route.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_route_forbidden(self):
        route = init_sample_route()
        res = self.client.delete(detail_url(route.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = init_sample_superuser()
        self.client.force_authenticate(self.user)

    def test_list_routes(self):
        init_sample_route()
        init_sample_route()
        res = self.client.get(ROUTE_URL)

        routes = Route.objects.order_by("source", "destination")
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_route_detail(self):
        init_sample_route()
        route = init_sample_route()
        res = self.client.get(detail_url(route.id))

        serializer = RouteDetailSerializer(route)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route(self):
        airport1 = init_sample_airport(name="Sample airport1")
        airport2 = init_sample_airport(name="Sample airport2")
        payload = {"source": airport1.id, "destination": airport2.id, "distance": 999 }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        route = Route.objects.get(id=res.data["id"])
        serializer = RouteSerializer(route)
        for key in payload.keys():
            self.assertEqual(serializer.data.get(key), payload.get(key))

    def test_update_route(self):
        route = init_sample_route()
        airport3 = init_sample_airport(name="Sample airport3")
        airport4 = init_sample_airport(name="Sample airport4")

        payload = {"id": route.id, "source": airport3.id, "destination": airport4.id, "distance": 777}
        res = self.client.put(detail_url(route.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        route_updated = Route.objects.get(id=route.id)
        serializer = RouteSerializer(route_updated)
        self.assertEqual(serializer.data, payload)

    def test_delete_route(self):
        route = init_sample_route()
        res = self.client.delete(detail_url(route.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
