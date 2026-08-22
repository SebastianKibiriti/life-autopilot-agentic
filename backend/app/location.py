from typing import Protocol
from datetime import datetime, timezone
from .models import Location, LocationProvider


class LocationRepository(Protocol):
    def save_location(self, student_id: str, location: Location) -> Location:
        ...

    def get_current_location(self, student_id: str) -> Location | None:
        ...


class InMemoryLocationRepository:
    def __init__(self) -> None:
        self._locations: dict[str, Location] = {}

    def save_location(self, student_id: str, location: Location) -> Location:
        if not student_id.strip():
            raise ValueError("student_id must not be empty")
        self._locations[student_id] = location.model_copy(deep=True)
        return self._locations[student_id]

    def get_current_location(self, student_id: str) -> Location | None:
        loc = self._locations.get(student_id)
        return loc.model_copy(deep=True) if loc else None


class FirestoreLocationRepository:
    def __init__(self, client) -> None:
        self.client = client

    def _doc(self, student_id: str):
        if not student_id.strip():
            raise ValueError("student_id must not be empty")
        return (
            self.client.collection("students")
            .document(student_id)
            .collection("context")
            .document("location")
        )

    def save_location(self, student_id: str, location: Location) -> Location:
        doc = self._doc(student_id)
        doc.set(location.model_dump(mode="json"))
        return location.model_copy(deep=True)

    def get_current_location(self, student_id: str) -> Location | None:
        doc = self._doc(student_id)
        snapshot = doc.get()
        if not snapshot.exists:
            return None
        data = snapshot.to_dict()
        return Location.model_validate(data)
