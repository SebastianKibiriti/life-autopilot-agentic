import math
import os
from datetime import datetime, timezone
import httpx

from .models import (
    Destination,
    DestinationProvider,
    Location,
    RouteProvider,
    TravelEstimate,
)


class PlacesResolver:
    """Resolves human-readable destinations to coordinates."""

    DEFAULT_CAMPUS_PLACES = {
        "engineering building b": (37.4275, -122.1697, "Engineering Building B, Stanford, CA"),
        "engineering building a": (37.4280, -122.1700, "Engineering Building A, Stanford, CA"),
        "building c": (37.4265, -122.1680, "Building C, Science Quad, Stanford, CA"),
        "room a": (37.4280, -122.1700, "Room A, Engineering Quad"),
        "room b": (37.4275, -122.1697, "Room B, Engineering Quad"),
        "library": (37.4250, -122.1650, "Main Campus Library"),
        "student union": (37.4240, -122.1690, "Student Union Building"),
        "lakeside office": (-26.1500, 28.0500, "Lakeside Office, Johannesburg"),
    }

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("PLACES_API_KEY")
        self._cache: dict[str, Destination] = {}

    def resolve(self, query: str) -> Destination | None:
        cleaned = query.strip().lower()
        if not cleaned:
            return None
        if cleaned in self._cache:
            return self._cache[cleaned]

        if cleaned in self.DEFAULT_CAMPUS_PLACES:
            lat, lng, addr = self.DEFAULT_CAMPUS_PLACES[cleaned]
            dest = Destination(
                label=query,
                latitude=lat,
                longitude=lng,
                formatted_address=addr,
                resolution_confidence=1.0,
                provider=DestinationProvider.CACHED,
            )
            self._cache[cleaned] = dest
            return dest

        if self.api_key:
            try:
                with httpx.Client(timeout=5.0) as client:
                    resp = client.post(
                        "https://places.googleapis.com/v1/places:searchText",
                        headers={
                            "Content-Type": "application/json",
                            "X-Goog-Api-Key": self.api_key,
                            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
                        },
                        json={"textQuery": query},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        places = data.get("places", [])
                        if places:
                            place = places[0]
                            loc = place.get("location", {})
                            latitude = loc.get("latitude")
                            longitude = loc.get("longitude")
                            if latitude is None or longitude is None:
                                return None
                            dest = Destination(
                                label=place.get("displayName", {}).get("text", query),
                                latitude=latitude,
                                longitude=longitude,
                                formatted_address=place.get("formattedAddress"),
                                resolution_confidence=0.95,
                                provider=DestinationProvider.PLACES,
                            )
                            self._cache[cleaned] = dest
                            return dest
            except Exception:
                return None

        return None


class RoutesEstimator:
    """Estimates walking travel duration and distance with Google Routes API or fallback."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("ROUTES_API_KEY")

    def estimate_walking(
        self, origin: Location, destination: Destination
    ) -> TravelEstimate:
        # 1. If API Key present, try Google Routes API
        if self.api_key:
            try:
                with httpx.Client(timeout=5.0) as client:
                    resp = client.post(
                        "https://routes.googleapis.com/directions/v2:computeRoutes",
                        headers={
                            "Content-Type": "application/json",
                            "X-Goog-Api-Key": self.api_key,
                            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters",
                        },
                        json={
                            "origin": {
                                "location": {
                                    "latLng": {
                                        "latitude": origin.latitude,
                                        "longitude": origin.longitude,
                                    }
                                }
                            },
                            "destination": {
                                "location": {
                                    "latLng": {
                                        "latitude": destination.latitude,
                                        "longitude": destination.longitude,
                                    }
                                }
                            },
                            "travelMode": "WALK",
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        routes = data.get("routes", [])
                        if routes:
                            route = routes[0]
                            dist_meters = route.get("distanceMeters", 0)
                            dur_str = route.get("duration", "0s").rstrip("s")
                            dur_seconds = int(float(dur_str))
                            dur_minutes = max(1, math.ceil(dur_seconds / 60))
                            return TravelEstimate(
                                origin=origin,
                                destination=destination,
                                mode="walking",
                                distance_meters=dist_meters,
                                duration_seconds=dur_seconds,
                                duration_minutes=dur_minutes,
                                provider=RouteProvider.ROUTES,
                                estimated_at=datetime.now(timezone.utc),
                            )
            except Exception:
                pass

        # 2. High accuracy Haversine walking calculation fallback
        lat1, lon1 = origin.latitude, origin.longitude
        lat2, lon2 = destination.latitude, destination.longitude
        r = 6371000  # Earth radius in meters

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        direct_distance = r * c

        # Average pedestrian walking speed: ~1.35 m/s (~4.86 km/h)
        # Factor in urban pedestrian path network factor ~1.25
        pedestrian_distance = int(direct_distance * 1.25)
        walking_speed_mps = 1.35
        duration_seconds = int(pedestrian_distance / walking_speed_mps)
        duration_minutes = max(1, math.ceil(duration_seconds / 60))

        return TravelEstimate(
            origin=origin,
            destination=destination,
            mode="walking",
            distance_meters=pedestrian_distance,
            duration_seconds=duration_seconds,
            duration_minutes=duration_minutes,
            provider=RouteProvider.FALLBACK,
            estimated_at=datetime.now(timezone.utc),
        )
