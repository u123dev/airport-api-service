from django.urls import path, include
from rest_framework import routers

from airport.views import (
    CountryViewSet, CityViewSet, AirportViewSet, RouteViewSet, CrewViewSet, AirplaneTypeViewSet, AirplaneViewSet,
    FlightViewSet, OrderViewSet,

)

router = routers.DefaultRouter()
router.register("countries", CountryViewSet)
router.register("cities", CityViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("crews", CrewViewSet)
router.register("airplane-types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)


urlpatterns = [path("", include(router.urls))]

app_name = "airport"
