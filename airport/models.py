import pathlib
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


def set_filename(new_filename, filename: str) -> pathlib.Path:
    return (f"{slugify(new_filename)}-{uuid.uuid4()}"
            + pathlib.Path(filename).suffix)


def crew_image_path(instance, filename: str) -> pathlib.Path:
    return pathlib.Path("upload/crews") / pathlib.Path(
        set_filename(instance.full_name, filename)
    )


def airplane_image_path(instance, filename: str) -> pathlib.Path:
    return pathlib.Path("upload/airplanes") / pathlib.Path(
        set_filename(
            f"{instance.name} {instance.airplane_type.name}",
            filename
        )
    )


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255, unique=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="cities"
    )

    class Meta:
        ordering = ("name", )
        verbose_name_plural = "cities"

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=255, unique=True)
    closest_big_city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="airports",
    )

    class Meta:
        ordering = ("closest_big_city", "name", )

    def __str__(self):
        return f"{self.name} | {self.closest_big_city.name}"


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="src_routes"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="dest_routes"
    )
    distance = models.PositiveIntegerField()

    class Meta:
        ordering = ("source", "destination", )
        constraints = [
            models.UniqueConstraint(
                fields=("source", "destination"),
                name="unique_route_src_dest"
            )
        ]

    def __str__(self):
        return f"{self.source} -> {self.destination}"


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to=crew_image_path, blank=True, null=True)

    class Meta:
        ordering = ("last_name",)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )
    airplane_photo = models.ImageField(
        upload_to=airplane_image_path,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ("airplane_type", "name",)

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name} | {self.airplane_type.name}"


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    crew = models.ManyToManyField(Crew, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ("-departure_time", )
        constraints = [
            models.CheckConstraint(
                check=models.Q(arrival_time__gt=F("departure_time")),
                name="check"
            ),
            models.UniqueConstraint(
                fields=("airplane", "departure_time"),
                name="unique_airplane_departure"
            )
        ]

    def __str__(self):
        return f"{self.departure_time} - {self.arrival_time} | {self.route}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="orders"
    )

    class Meta:
        ordering = ("-created_at", )

    def __str__(self):
        return f"{self.id} | {self.created_at}"


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {airplane_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    class Meta:
        ordering = ("flight", "row", "seat")
        constraints = [
            models.UniqueConstraint(
                fields=("flight", "row", "seat"),
                name="unique_flight_row_seat"
            )
        ]

    def __str__(self):
        return (
            f"Order: {self.order} | "
            f"Flight: {self.flight} - (row: {self.row}, seat: {self.seat})"
        )
