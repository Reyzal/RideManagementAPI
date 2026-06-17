from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from django.utils import timezone
from rest_framework.viewsets import ModelViewSet

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
    filter_backends = [DjangoFilterBackend]
    filterset_class = RideFilter

    def get_queryset(self):
        last_24_hours = timezone.now() - timedelta(hours=24)

        todays_events_queryset = (
            RideEvent.objects
            .filter(created_at__gte=last_24_hours)
            .order_by("-created_at")
        )

        return (
            Ride.objects
            .select_related("id_rider", "id_driver")
            .prefetch_related(
                Prefetch(
                    "ride_events",
                    queryset=todays_events_queryset,
                    to_attr="todays_ride_events",
                )
            )
            .order_by("id_ride")
        )


class RideEventViewSet(ModelViewSet):
    authentication_classes = [ApiTokenAuthentication]
    permission_classes = [IsAdminRole]

    queryset = RideEvent.objects.select_related("id_ride").order_by("id_ride_event")
    serializer_class = RideEventSerializer
    

