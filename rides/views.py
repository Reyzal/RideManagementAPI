from django.db.models import F, FloatField, Value, Prefetch
from django.db.models.functions import ACos, Cos, Radians, Sin
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter

from .authentication import ApiTokenAuthentication
from .filters import RideFilter
from .models import Ride, RideEvent, User
from .permissions import IsAdminRole
from .serializers import RideEventSerializer, RideSerializer, UserSerializer




class UserViewSet(ModelViewSet):
    authentication_classes = [ApiTokenAuthentication]
    permission_classes = [IsAdminRole]

    queryset = User.objects.all().order_by("id_user")
    serializer_class = UserSerializer


class RideViewSet(ModelViewSet):
    authentication_classes = [ApiTokenAuthentication]
    permission_classes = [IsAdminRole]

    serializer_class = RideSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = RideFilter
    ordering_fields = ["pickup_time", "id_ride"]
    ordering = ["id_ride"]

    def get_queryset(self):
        last_24_hours = timezone.now() - timedelta(hours=24)

        todays_events_queryset = (
            RideEvent.objects
            .filter(created_at__gte=last_24_hours)
            .order_by("-created_at")
        )

        queryset = (
            Ride.objects
            .select_related("id_rider", "id_driver")
            .prefetch_related(
                Prefetch(
                    "ride_events",
                    queryset=todays_events_queryset,
                    to_attr="todays_ride_events",
                )
            )
        )

        sort = self.request.query_params.get("sort")

        if sort == "distance":
            queryset = self._order_by_pickup_distance(queryset)

        return queryset

    def _order_by_pickup_distance(self, queryset):
        lat = self.request.query_params.get("lat")
        lng = self.request.query_params.get("lng")

        if lat is None or lng is None:
            raise ValidationError(
                "lat and lng query parameters are required when sort=distance."
            )

        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            raise ValidationError("lat and lng must be valid numbers.")

        if not -90 <= lat <= 90:
            raise ValidationError("lat must be between -90 and 90.")

        if not -180 <= lng <= 180:
            raise ValidationError("lng must be between -180 and 180.")

        # Haversine-style great-circle distance in kilometers.
        # This is calculated in SQL so pagination still works correctly.
        distance_expression = (
            Value(6371.0, output_field=FloatField())
            * ACos(
                Cos(Radians(Value(lat, output_field=FloatField())))
                * Cos(Radians(F("pickup_latitude")))
                * Cos(
                    Radians(F("pickup_longitude"))
                    - Radians(Value(lng, output_field=FloatField()))
                )
                + Sin(Radians(Value(lat, output_field=FloatField())))
                * Sin(Radians(F("pickup_latitude")))
            )
        )

        return (
            queryset
            .annotate(distance_km=distance_expression)
            .order_by("distance_km", "id_ride")
        )

class RideEventViewSet(ModelViewSet):
    authentication_classes = [ApiTokenAuthentication]
    permission_classes = [IsAdminRole]

    queryset = RideEvent.objects.select_related("id_ride").order_by("id_ride_event")
    serializer_class = RideEventSerializer
    

