from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    Country,
    City,
    Airport,
    Route,
    Crew,
    AirplaneType,
    Airplane,
    Flight,
    Ticket,
    Order
)


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ("id", "name", "country")


class CityListSerializer(CitySerializer):
    country = serializers.SlugRelatedField(slug_field="name", read_only=True)


class AirportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class AirportListSerializer(AirportSerializer):
    closest_big_city = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True
    )


class RouteSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        if attrs.get("source") == attrs.get("destination"):
            raise serializers.ValidationError(
                "Source and Destination must be different !"
            )
        return attrs

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    destination = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True
    )


class RouteDetailSerializer(RouteSerializer):
    source = AirportListSerializer(read_only=True)
    destination = AirportListSerializer(read_only=True)


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name", "photo")
        read_only_fields = ("full_name", "photo",)


class CrewPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "full_name", "photo")
        read_only_fields = ("full_name", )


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "airplane_photo"
        )
        read_only_fields = ("airplane_photo", )


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True
    )


class AirplanePhotoSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True
    )

    class Meta:
        model = Airplane
        fields = ("id", "name", "airplane_type", "airplane_photo")
        read_only_fields = ("name", "airplane_type", )


################
class FlightSerializer(serializers.ModelSerializer):
    # crew = CrewSerializer(many=True, read_only=True)
    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "route",
            "airplane",
            "crew"
        )


class FlightListSerializer(FlightSerializer):
    route_source = serializers.CharField(
        source="route.source.name",
        read_only=True
    )
    route_destination = serializers.CharField(
        source="route.destination.name",
        read_only=True
    )
    airplane_name = serializers.CharField(
        source="airplane.name",
        read_only=True
    )
    airplane_image = serializers.ImageField(
        source="airplane.image",
        read_only=True
    )
    crew = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )
    # crew = CrewSerializer(many=True, read_only=True)
    # cinema_hall_name = serializers.CharField(
    #     source="cinema_hall.name", read_only=True
    # )
    airplane_capacity = serializers.IntegerField(
        source="airplane.capacity", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time", "arrival_time",
            "route_source",
            "route_destination",
            "airplane_name",
            "airplane_capacity",
            "tickets_available",
            "airplane_image",
            "crew",
        )


##########
class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


############
class FlightDetailSerializer(FlightSerializer):
    route = RouteDetailSerializer(many=False, read_only=True)
    airplane = AirplaneListSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True)
    taken_places = TicketSeatsSerializer(
        source="tickets", many=True, read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "route",
            "taken_places",
            "airplane",
            "crew"
        )


############
class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
