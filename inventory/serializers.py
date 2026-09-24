from datetime import date
from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from .models import Booking, Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            "id",
            "name",
            "brand",
            "year",
            "price_per_day",
            "fuel_type",
            "is_available",
        ]
        read_only_fields = ["id"]

    def validate_year(self, value):
        current_year = date.today().year
        if value < 1886 or value > current_year + 1:
            raise serializers.ValidationError(
                f"Year must be between 1886 and {current_year + 1}."
            )
        return value

    def validate_price_per_day(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError(
                "price_per_day must be greater than 0."
            )
        return value


class BookingSerializer(serializers.ModelSerializer):
    vehicle_name = serializers.CharField(
        source="vehicle.name",
        read_only=True,
    )
    brand = serializers.CharField(
        source="vehicle.brand",
        read_only=True,
    )
    rental_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "vehicle",
            "vehicle_name",
            "brand",
            "customer_name",
            "customer_phone",
            "start_date",
            "end_date",
            "rental_days",
            "total_amount",
        ]
        read_only_fields = [
            "id",
            "vehicle_name",
            "brand",
            "rental_days",
            "total_amount",
        ]

    def validate_customer_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "Customer name cannot be empty."
            )
        return value

    def validate_customer_phone(self, value):
        value = value.strip()
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError(
                "Phone number must contain exactly 10 digits."
            )
        return value

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and start_date < date.today():
            raise serializers.ValidationError(
                {"start_date": "Start date cannot be in the past."}
            )

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )

        vehicle = attrs.get("vehicle")

        if vehicle:
            if not vehicle.is_available:
                raise serializers.ValidationError(
                    {"vehicle": "This vehicle is currently unavailable."}
                )

            if start_date and end_date:
                overlapping = Booking.objects.filter(
                    vehicle=vehicle,
                    start_date__lt=end_date,
                    end_date__gt=start_date,
                )

                # Exclude current booking if this serializer is ever reused
                # for updates.
                if self.instance:
                    overlapping = overlapping.exclude(pk=self.instance.pk)

                if overlapping.exists():
                    raise serializers.ValidationError(
                        {
                            "vehicle": (
                                "This vehicle is already booked for "
                                "the selected date range."
                            )
                        }
                    )

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            vehicle = Vehicle.objects.select_for_update().get(
                pk=validated_data["vehicle"].pk
            )

            if not vehicle.is_available:
                raise serializers.ValidationError(
                    {"vehicle": "This vehicle is currently unavailable."}
                )

            start_date = validated_data["start_date"]
            end_date = validated_data["end_date"]

            overlapping = Booking.objects.filter(
                vehicle=vehicle,
                start_date__lt=end_date,
                end_date__gt=start_date,
            )

            if overlapping.exists():
                raise serializers.ValidationError(
                    {
                        "vehicle": (
                            "This vehicle is already booked for "
                            "the selected date range."
                        )
                    }
                )

            days = (end_date - start_date).days
            total_amount = (
                Decimal(days) * vehicle.price_per_day
            )

            booking = Booking.objects.create(
                **validated_data,
                total_amount=total_amount,
            )

            # Requirement: after booking, vehicle becomes unavailable.
            vehicle.is_available = False
            vehicle.save(update_fields=["is_available"])

            return booking
