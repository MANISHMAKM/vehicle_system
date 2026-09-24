from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .models import Booking, Vehicle
from .serializers import BookingSerializer, VehicleSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    """
    Vehicle endpoints:
    GET    /api/vehicles/
    POST   /api/vehicles/
    GET    /api/vehicles/<id>/
    PUT    /api/vehicles/<id>/
    PATCH  /api/vehicles/<id>/
    DELETE /api/vehicles/<id>/
    """

    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()

        brand = self.request.query_params.get("brand")
        fuel_type = self.request.query_params.get("fuel_type")
        is_available = self.request.query_params.get("is_available")

        if brand:
            queryset = queryset.filter(brand__iexact=brand)

        if fuel_type:
            queryset = queryset.filter(fuel_type__iexact=fuel_type)

        if is_available is not None:
            value = is_available.lower()

            if value in ["true", "1", "yes"]:
                queryset = queryset.filter(is_available=True)
            elif value in ["false", "0", "no"]:
                queryset = queryset.filter(is_available=False)

        return queryset


class BookingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Booking endpoints:
    GET  /api/bookings/
    POST /api/bookings/
    GET  /api/bookings/<id>/
    """

    queryset = Booking.objects.select_related("vehicle").all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        serializer.save()
