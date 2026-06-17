import secrets

from django.db import models


class User(models.Model):
    id_user = models.AutoField(primary_key=True)
    role = models.CharField(max_length=50)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(db_index=True)
    phone_number = models.CharField(max_length=50)

    class Meta:
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} <{self.email}>"


class Ride(models.Model):
    id_ride = models.AutoField(primary_key=True)
    status = models.CharField(max_length=50, db_index=True)

    id_rider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="rides_as_rider",
        db_column="id_rider",
    )
    id_driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="rides_as_driver",
        db_column="id_driver",
    )

    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["pickup_time"]),
            models.Index(fields=["pickup_latitude", "pickup_longitude"]),
            models.Index(fields=["id_rider", "status"]),
        ]

    def __str__(self) -> str:
        return f"Ride {self.id_ride} - {self.status}"


class RideEvent(models.Model):
    id_ride_event = models.AutoField(primary_key=True)
    id_ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name="ride_events",
        db_column="id_ride",
    )
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["id_ride", "created_at"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["description"]),
        ]

    def __str__(self) -> str:
        return f"RideEvent {self.id_ride_event} - Ride {self.id_ride_id}"
    
    
class ApiToken(models.Model):
    key = models.CharField(max_length=64, unique=True, db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="api_tokens",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_key() -> str:
        return secrets.token_hex(32)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Token for {self.user.email}"