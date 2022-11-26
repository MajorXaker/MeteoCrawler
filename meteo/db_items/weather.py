import datetime

import sqlalchemy as sa

from meteo.db_items.base_engine import Model


class Weather(Model):
    __tablename__ = "weathers"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    timedate = sa.Column(sa.DateTime, nullable=False)
    weather_type_raw = sa.Column(sa.String)
    weather_type = sa.Column(sa.String)
    precipitation_type = sa.Column(sa.String)
    weather_quality = sa.Column(sa.String, nullable=False)
    temp_min = sa.Column(sa.Integer, nullable=False)
    temp_max = sa.Column(sa.Integer, nullable=False)
    city_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("cities.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    atm_pressure_min = sa.Column(sa.Integer)
    atm_pressure_max = sa.Column(sa.Integer)
    humidity_min = sa.Column(sa.Integer)
    humidity_max = sa.Column(sa.Integer)
    wind_speed_min = sa.Column(sa.Integer)
    wind_speed_max = sa.Column(sa.Integer)
    wind_direction = sa.Column(sa.String)
    wind_unstable = sa.Column(sa.Boolean)
    precipitation_per_hour = sa.Column(sa.Float)
    snow_level = sa.Column(sa.Float)
