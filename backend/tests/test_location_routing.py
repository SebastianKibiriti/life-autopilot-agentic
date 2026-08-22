import unittest
from datetime import datetime, timezone

from app.models import Location, LocationProvider, Destination, DestinationProvider, RouteProvider
from app.location import InMemoryLocationRepository
from app.routing import PlacesResolver, RoutesEstimator


class LocationAndRoutingTests(unittest.TestCase):
    def test_location_repository(self):
        repo = InMemoryLocationRepository()
        self.assertIsNone(repo.get_current_location("student-1"))

        loc = Location(latitude=37.4275, longitude=-122.1697, provider=LocationProvider.GPS)
        saved = repo.save_location("student-1", loc)
        self.assertEqual(saved.latitude, 37.4275)

        fetched = repo.get_current_location("student-1")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.latitude, 37.4275)

    def test_places_resolver_cached(self):
        resolver = PlacesResolver()
        dest = resolver.resolve("Engineering Building B")
        self.assertEqual(dest.label, "Engineering Building B")
        self.assertEqual(dest.latitude, 37.4275)
        self.assertEqual(dest.provider, DestinationProvider.CACHED)

    def test_places_resolver_unknown_fallback(self):
        resolver = PlacesResolver()
        dest = resolver.resolve("Unknown Room 999")
        self.assertIsNone(dest)

    def test_routes_estimator_walking_fallback(self):
        estimator = RoutesEstimator()
        origin = Location(latitude=37.4200, longitude=-122.1600)
        dest = Destination(label="Target Hall", latitude=37.4275, longitude=-122.1697)

        estimate = estimator.estimate_walking(origin, dest)
        self.assertGreater(estimate.distance_meters, 0)
        self.assertGreater(estimate.duration_seconds, 0)
        self.assertGreater(estimate.duration_minutes, 0)
        self.assertEqual(estimate.provider, RouteProvider.FALLBACK)


if __name__ == "__main__":
    unittest.main()
