"""Condições climáticas resumidas de uma partida."""

from ultrastats_ai.domain.shared.enums import DomainEnum


class WeatherCondition(DomainEnum):
    """Classifica o clima observado no local da partida."""

    SUNNY = "sunny"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    OVERCAST = "overcast"
    LIGHT_RAIN = "light_rain"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    STORM = "storm"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"
    HAIL = "hail"
    FOG = "fog"
    MIST = "mist"
    WINDY = "windy"
    HOT = "hot"
    COLD = "cold"
    OTHER = "other"
    UNKNOWN = "unknown"
