from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, VehicleViewSet

class OptionalSlashRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = "/?"


router = OptionalSlashRouter()
router.register(r"vehicles", VehicleViewSet, basename="vehicle")
router.register(r"bookings", BookingViewSet, basename="booking")

urlpatterns = router.urls

