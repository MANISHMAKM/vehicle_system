from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, VehicleViewSet

router = DefaultRouter()
router.register(r"vehicles", VehicleViewSet, basename="vehicle")
router.register(r"bookings", BookingViewSet, basename="booking")

urlpatterns = router.urls
