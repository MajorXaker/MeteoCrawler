from utils.base_enum import StrEnum


class WindDirection(StrEnum):
    SOUTH = "S"
    NORTH = "N"
    WEST = "W"
    EAST = "E"
    SOUTH_EAST = "SE"
    SOUTH_WEST = "SW"
    NORTH_EAST = "NE"
    NORTH_WEST = "NW"

class WeatherType(StrEnum):
    RAIN = "Rain"
    SUNNY = "Sunny"
    # TODO make this matching


