"""Optional live context used to make departure messages more useful."""
import os
from datetime import datetime

import httpx

from .models import Destination, Location


def departure_context(*, now: datetime, origin: Location | None, destination: Destination | None) -> tuple[str, str]:
    """Return concise observations; never block or fail the autonomous decision."""
    weather = os.getenv("WEATHER_OBSERVATION")
    traffic = os.getenv("TRAFFIC_OBSERVATION")

    if not weather and origin and os.getenv("OPEN_METEO_ENABLED", "false").lower() == "true":
        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={"latitude": origin.latitude, "longitude": origin.longitude,
                            "current": "temperature_2m,precipitation,rain,wind_speed_10m"},
                )
                response.raise_for_status()
                current = response.json().get("current", {})
                weather = (f"{current.get('temperature_2m', 'unknown')}°C; "
                           f"rain {current.get('rain', 0)} mm; "
                           f"wind {current.get('wind_speed_10m', 'unknown')} km/h")
        except Exception:
            weather = None

    if not traffic and origin and destination and os.getenv("ROUTES_API_KEY"):
        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.post(
                    "https://routes.googleapis.com/directions/v2:computeRoutes",
                    headers={"X-Goog-Api-Key": os.environ["ROUTES_API_KEY"],
                             "X-Goog-FieldMask": "routes.duration,routes.staticDuration"},
                    json={"origin": {"location": {"latLng": {"latitude": origin.latitude, "longitude": origin.longitude}}},
                          "destination": {"location": {"latLng": {"latitude": destination.latitude, "longitude": destination.longitude}}},
                          "travelMode": "DRIVE", "routingPreference": "TRAFFIC_AWARE"},
                )
                response.raise_for_status()
                route = response.json().get("routes", [])[0]
                traffic = f"traffic-aware driving estimate {route.get('duration', 'unavailable')}"
        except Exception:
            traffic = None

    return (
        weather or "Weather forecast unavailable",
        traffic or "Traffic conditions unavailable",
    )
