from django.db.models import F, Count, Q
from django_filters import rest_framework as filters
from django_filters.filters import DateFromToRangeFilter
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from airport.models import (
    Country,
    City,
    Airport,
    Route,
    Crew,
    AirplaneType,
    Airplane,
    Flight,
    Order
)
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers import (
    CountrySerializer,
    CitySerializer,
    CityListSerializer,
    AirportListSerializer,
    AirportSerializer,
    RouteSerializer,
    RouteListSerializer,
    CrewSerializer,
    CrewPhotoSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplanePhotoSerializer,
    AirplaneListSerializer,
    FlightListSerializer,
    FlightSerializer,
    FlightDetailSerializer,
    RouteDetailSerializer,
    OrderSerializer,
    OrderListSerializer
)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            return qs.select_related("country")
        return qs

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return CityListSerializer
        return CitySerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            return qs.select_related("closest_big_city")
        return qs

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return AirportListSerializer
        return AirportSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action == "list":
            src_str = self.request.query_params.get("source")
            dest_str = self.request.query_params.get("destination")
            if src_str:
                queryset = queryset.filter(
                    Q(source__name__icontains=src_str)
                    | Q(source__closest_big_city__name__icontains=src_str)
                )
            if dest_str:
                queryset = queryset.filter(
                    Q(destination__name__icontains=dest_str)
                    | Q(
                        destination__closest_big_city__name__icontains=dest_str
                    )
                )
            return queryset.select_related(
                "source__closest_big_city",
                "destination__closest_big_city"
            )

        return queryset

    def get_serializer_class(self):
        if self.action in ("list", ):
            return RouteListSerializer
        if self.action in ("retrieve", ):
            return RouteDetailSerializer
        return RouteSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter by route source (ex. ?source=york)."
                            "Case-insensitive lookup that contains value",
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description="Filter by route destination "
                            "(ex. ?destination=hong)."
                            "Case-insensitive lookup that contains value",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "upload":
            return CrewPhotoSerializer
        return CrewSerializer

    @action(
        methods=["POST", "GET"],
        detail=True,
        url_path="photo",
        permission_classes=[IsAdminUser],
    )
    def upload(self, request, pk=None):
        """Endpoint for uploading photo to specific crew"""
        crew = self.get_object()
        serializer = self.get_serializer(crew, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().select_related("airplane_type")
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return AirplaneListSerializer
        if self.action == "upload":
            return AirplanePhotoSerializer
        return AirplaneSerializer

    @action(
        methods=["POST", "GET"],
        detail=True,
        url_path="image",
        permission_classes=[IsAdminUser],
    )
    def upload(self, request, pk=None):
        """Endpoint for uploading image to specific airplane"""
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class FlightFilter(filters.FilterSet):
    source = filters.CharFilter(
        field_name="route__source__name",
        lookup_expr="icontains"
    )
    destination = filters.CharFilter(
        field_name="route__destination__name",
        lookup_expr="icontains"
    )
    departure_date = DateFromToRangeFilter(field_name="departure_time")
    arrival_date = DateFromToRangeFilter(field_name="arrival_time")

    class Meta:
        model = Flight
        fields = [
            "source",
            "destination",
            "departure_date",
            "arrival_date"
        ]


class FlightViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = (
        Flight.objects.all()
        .select_related("route", "airplane")
        .annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        ).prefetch_related("crew")
    )
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FlightFilter

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "departure_date_after",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter by departure date after "
                    "(ex. ?departure_date_after=2022-10-23)"
                ),
            ),
            OpenApiParameter(
                "departure_date_before",
                type=OpenApiTypes.DATE,
                description="Filter by departure date before "
                            "(ex. ?departure_date_before=2022-10-25)",
            ),
            OpenApiParameter(
                "arrival_date_after",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter by arrival date after "
                    "(ex. ?arrival_date_after=2022-10-27)"
                ),
            ),
            OpenApiParameter(
                "arrival_date_before",
                type=OpenApiTypes.DATE,
                description="Filter by arrival date before "
                            "(ex. ?arrival_date_before=2022-10-29)",
            ),
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter by route source (ex. ?source=york)."
                            "Case-insensitive lookup that contains value",
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description="Filter by route destination "
                            "(ex. ?destination=hong)."
                            "Case-insensitive lookup that contains value",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route",
        "tickets__flight__airplane",
        "tickets__flight__crew",
    )
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
