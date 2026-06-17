from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from rides.models import ApiToken, Ride, RideEvent, User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user():
    return User.objects.create(
        role="admin",
        first_name="Admin",
        last_name="User",
        email="admin@example.com",
        phone_number="09170000000",
    )


@pytest.fixture
def non_admin_user():
    return User.objects.create(
        role="rider",
        first_name="Normal",
        last_name="User",
        email="normal@example.com",
        phone_number="09171111111",
    )


@pytest.fixture
def admin_token(admin_user):
    return ApiToken.objects.create(user=admin_user)


@pytest.fixture
def non_admin_token(non_admin_user):
    return ApiToken.objects.create(user=non_admin_user)


@pytest.fixture
def rider():
    return User.objects.create(
        role="rider",
        first_name="Test",
        last_name="Rider",
        email="rider@example.com",
        phone_number="09172222222",
    )


@pytest.fixture
def second_rider():
    return User.objects.create(
        role="rider",
        first_name="Second",
        last_name="Rider",
        email="second.rider@example.com",
        phone_number="09173333333",
    )


@pytest.fixture
def driver():
    return User.objects.create(
        role="driver",
        first_name="Test",
        last_name="Driver",
        email="driver@example.com",
        phone_number="09174444444",
    )


@pytest.fixture
def rides(rider, second_rider, driver):
    ride_1 = Ride.objects.create(
        status="pickup",
        id_rider=rider,
        id_driver=driver,
        pickup_latitude=10.3157,
        pickup_longitude=123.8854,
        dropoff_latitude=10.2930,
        dropoff_longitude=123.9020,
        pickup_time=timezone.now() + timedelta(hours=2),
    )

    ride_2 = Ride.objects.create(
        status="dropoff",
        id_rider=second_rider,
        id_driver=driver,
        pickup_latitude=10.4000,
        pickup_longitude=123.9000,
        dropoff_latitude=10.2930,
        dropoff_longitude=123.9020,
        pickup_time=timezone.now() + timedelta(hours=1),
    )

    return ride_1, ride_2


def authorize(client, token):
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")


@pytest.mark.django_db
def test_ride_list_requires_authentication(api_client):
    response = api_client.get("/api/rides/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_ride_list_rejects_invalid_token(api_client):
    api_client.credentials(HTTP_AUTHORIZATION="Token invalid-token")

    response = api_client.get("/api/rides/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_ride_list_rejects_non_admin_user(api_client, non_admin_token):
    authorize(api_client, non_admin_token)

    response = api_client.get("/api/rides/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_ride_list_allows_admin_user(api_client, admin_token, rides):
    authorize(api_client, admin_token)

    response = api_client.get("/api/rides/")

    assert response.status_code == 200
    assert response.data["count"] == 2
    assert "results" in response.data


@pytest.mark.django_db
def test_ride_list_filters_by_status(api_client, admin_token, rides):
    authorize(api_client, admin_token)

    response = api_client.get("/api/rides/?status=pickup")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["status"] == "pickup"


@pytest.mark.django_db
def test_ride_list_filters_by_rider_email(api_client, admin_token, rides):
    authorize(api_client, admin_token)

    response = api_client.get("/api/rides/?rider_email=rider@example.com")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id_rider"]["email"] == "rider@example.com"


@pytest.mark.django_db
def test_ride_list_includes_only_todays_ride_events(api_client, admin_token, rides):
    authorize(api_client, admin_token)

    ride_1, _ = rides

    RideEvent.objects.create(
        id_ride=ride_1,
        description="Status changed to pickup",
        created_at=timezone.now(),
    )

    RideEvent.objects.create(
        id_ride=ride_1,
        description="Old event should not show",
        created_at=timezone.now() - timedelta(days=3),
    )

    response = api_client.get("/api/rides/?status=pickup")

    assert response.status_code == 200

    events = response.data["results"][0]["todays_ride_events"]
    descriptions = [event["description"] for event in events]

    assert "Status changed to pickup" in descriptions
    assert "Old event should not show" not in descriptions


@pytest.mark.django_db
def test_ride_list_orders_by_pickup_time_ascending(api_client, admin_token, rides):
    authorize(api_client, admin_token)

    response = api_client.get("/api/rides/?ordering=pickup_time")

    assert response.status_code == 200

    result_ids = [item["id_ride"] for item in response.data["results"]]

    assert result_ids == [
        rides[1].id_ride,
        rides[0].id_ride,
    ]


@pytest.mark.django_db
def test_ride_list_orders_by_pickup_time_descending(api_client, admin_token, rides):
    authorize(api_client, admin_token)

    response = api_client.get("/api/rides/?ordering=-pickup_time")

    assert response.status_code == 200

    result_ids = [item["id_ride"] for item in response.data["results"]]

    assert result_ids == [
        rides[0].id_ride,
        rides[1].id_ride,
    ]


@pytest.mark.django_db
def test_ride_list_sorts_by_distance(api_client, admin_token, rides):
    authorize(api_client, admin_token)

    response = api_client.get("/api/rides/?sort=distance&lat=10.3157&lng=123.8854")

    assert response.status_code == 200

    results = response.data["results"]

    assert results[0]["id_ride"] == rides[0].id_ride
    assert "distance_km" in results[0]


@pytest.mark.django_db
def test_distance_sort_requires_lat_and_lng(api_client, admin_token, rides):
    authorize(api_client, admin_token)

    response = api_client.get("/api/rides/?sort=distance")

    assert response.status_code == 400


@pytest.mark.django_db
def test_distance_sort_rejects_invalid_latitude(api_client, admin_token, rides):
    authorize(api_client, admin_token)

    response = api_client.get("/api/rides/?sort=distance&lat=999&lng=123.8854")

    assert response.status_code == 400


@pytest.mark.django_db
def test_ride_list_query_count_is_low(
    api_client,
    admin_token,
    rides,
    django_assert_num_queries,
):
    authorize(api_client, admin_token)

    for ride in rides:
        RideEvent.objects.create(
            id_ride=ride,
            description="Status changed to pickup",
            created_at=timezone.now(),
        )

    # Expected:
    # 1 query = API token + user
    # 1 query = pagination COUNT
    # 1 query = rides + rider + driver via select_related
    # 1 query = today's ride events via filtered prefetch
    with django_assert_num_queries(4):
        response = api_client.get("/api/rides/")

    assert response.status_code == 200