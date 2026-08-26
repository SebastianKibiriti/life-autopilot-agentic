from .models import CampusPlace


PLACES = [
    CampusPlace(canonical_name="Nutrition Building N204", aliases=["N204", "Nutrition 204", "Nutrition Building Room 204"], latitude=-33.9605, longitude=22.4608, confidence=0.98),
    CampusPlace(canonical_name="Campus Cycling Track", aliases=["cycling track", "cycle track", "fitness track"], latitude=-33.9580, longitude=22.4650, confidence=0.95),
]


def resolve_campus(query: str):
    q = query.strip().lower()
    for place in PLACES:
        if q == place.canonical_name.lower() or q in [a.lower() for a in place.aliases]:
            return place
    return None
