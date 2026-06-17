from rest_framework.viewsets import ModelViewSet

from .authentication import ApiTokenAuthentication
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

    def get_queryset(self):
        return (
            Ride.objects
            .select_related("id_rider", "id_driver")
            .order_by("id_ride")
        )


class RideEventViewSet(ModelViewSet):
    authentication_classes = [ApiTokenAuthentication]
    permission_classes = [IsAdminRole]

    queryset = RideEvent.objects.select_related("id_ride").order_by("id_ride_event")
    serializer_class = RideEventSerializer