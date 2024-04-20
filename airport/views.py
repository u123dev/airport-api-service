from django.db.models import F, Count, Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from airport.models import Country, City, Airport, Route, Crew, AirplaneType, Airplane, Flight, Order
from airport.serializers import CountrySerializer, CitySerializer, CityListSerializer, AirportListSerializer, \
    AirportSerializer, RouteSerializer, RouteListSerializer, CrewSerializer, CrewPhotoSerializer, \
    AirplaneTypeSerializer, AirplaneSerializer, AirplanePhotoSerializer, AirplaneListSerializer, FlightListSerializer, \
    FlightSerializer, FlightDetailSerializer, RouteDetailSerializer, OrderSerializer, OrderListSerializer


class CountryViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = City.objects.all()
    # serializer_class = CityListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            return qs.select_related("country")
        return qs

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return CityListSerializer
        return CitySerializer


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.all()
    # serializer_class = AirportListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            return qs.select_related("closest_big_city")
        return qs

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return AirportListSerializer
        return AirportSerializer


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.all()
    # serializer_class = RouteListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action == "list":
            src_str = self.request.query_params.get("src")
            dest_str = self.request.query_params.get("dest")
            if src_str:
                queryset = queryset.filter(
                    Q(source__name__icontains=src_str) |
                    Q(source__closest_big_city__name__icontains=src_str)
                )
            if dest_str:
                queryset = queryset.filter(
                    Q(destination__name__icontains=dest_str) |
                    Q(destination__closest_big_city__name__icontains=dest_str)
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


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all()
    # serializer_class = CrewSerializer

    def get_serializer_class(self):
        if self.action == "upload":
            return CrewPhotoSerializer
        return CrewSerializer

    @action(
        methods=["POST", "GET"],
        detail=True,
        url_path="photo",
        # permission_classes=[IsAdminUser],
    )
    def upload(self, request, pk=None):
        """Endpoint for uploading photo to specific crew"""
        crew = self.get_object()
        serializer = self.get_serializer(crew, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airplane.objects.all()
    # serializer_class = AirplaneSerializer

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
        # permission_classes=[IsAdminUser],
    )
    def upload(self, request, pk=None):
        """Endpoint for uploading image to specific airplane"""
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


########

class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.all()
        .select_related("route", "airplane")
        .annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        )
    )
    serializer_class = FlightSerializer
    # permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer


#############
class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route", "tickets__flight__airplane"
    )
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    # permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
