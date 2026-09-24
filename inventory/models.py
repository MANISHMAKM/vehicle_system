from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models


class Vehicle(models.Model):
    class FuelType(models.TextChoices):
        PETROL = "Petrol", "Petrol"
        DIESEL = "Diesel", "Diesel"
        ELECTRIC = "Electric", "Electric"
        HYBRID = "Hybrid", "Hybrid"

    name = models.CharField(max_length=150)
    brand = models.CharField(max_length=100)
    year = models.IntegerField()
    price_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    fuel_type = models.CharField(
        max_length=20,
        choices=FuelType.choices,
    )
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.brand} {self.name}"


class Booking(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=10)
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.customer_name} - {self.vehicle}"

    @property
    def rental_days(self):
        return (self.end_date - self.start_date).days
