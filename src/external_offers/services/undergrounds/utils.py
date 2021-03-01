import math


EARTH_RADIUS = 6378137.0


def haversine(
    *,
    lon1: float,
    lat1: float,
    lon2: float,
    lat2: float
) -> float:
    """
    Вычисление расстояния между 2 координатами в метрах
    """
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    distance_lon = abs(lon2 - lon1)
    distance_lat = abs(lat2 - lat1)
    a = math.sin(distance_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(distance_lon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return c * EARTH_RADIUS
