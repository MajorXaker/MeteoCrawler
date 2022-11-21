import datetime
from dataclasses import dataclass
from typing import Optional

import arrow
import pydantic

from .enums import WindDirection, WeatherType


class Span:
    min: int | float
    max: int | float

    def __init__(self, vals: list | tuple | set):
        self.max = max(vals)
        self.min = min(vals)

    def __repr__(self):
        return f"Span (min={self.min}, max={self.max})"


class Weather(pydantic.BaseModel):
    class Config:
        arbitrary_types_allowed = True

    timedate: datetime.datetime
    weather_type_raw: str
    weather_type: Optional[WeatherType]
    temp: Span
    city_name: str
    atm_pressure: Span
    humidity: Optional[Span]
    wind_speed: Span
    wind_direction: WindDirection
    wind_unstable: Optional[bool]
    precipitation_per_hour: Optional[float]
    snow_level: Optional[int]
