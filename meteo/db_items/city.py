from meteo.db_items.base_engine import Model
import sqlalchemy as sa


class City(Model):
    __tablename__ = "cities"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String)
    coordinates_latitude = sa.Column(sa.Float)
    coordinates_longitude = sa.Column(sa.Float)
