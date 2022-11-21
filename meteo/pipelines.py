import re
import sqlalchemy as sa
from scrapy.exceptions import DropItem
from sqlalchemy.orm import Session

from meteo.db_items.city import City
from meteo.db_items.weather import Weather as DbWeather
from meteo.items.anecdote import Anecdote
from meteo.items.weather import Weather
from meteo.items.wise_phrase import WisePhrase
from utils.db import engine


class MeteoPipeline:
    def process_item(self, item, spider):
        if isinstance(item, Weather):
            item = self.process_weather_item(weather=item)
        elif isinstance(item, Anecdote):
            item = self.process_anecdote_item(item=item)
        elif isinstance(item, WisePhrase):
            item = self.process_wise_phrase_item(item=item)
        return item

    def process_weather_item(self, weather: Weather):
        db_item = {}
        with Session(engine) as session:
            city_id = session.execute(
                sa.select(City.id).where(City.name == weather.city_name)
            ).fetchone()
            if not city_id:
                raise DropItem("Weather for unknown city")

            for column_to_fill in DbWeather.__table__.columns:
                column_name = column_to_fill.key
                if column_name == "id":
                    continue
                min_or_max = re.findall("_min|_max", column_name)
                if min_or_max:
                    min_or_max = min_or_max[0].strip("_")
                    column_name = re.sub("_min|_max", "", column_name)
                    value = getattr(getattr(weather, column_name), min_or_max)
                else:
                    value = getattr(weather, column_name)
                db_item[column_to_fill] = value

            if self.is_new_value(session=city_id, datetime=weather.timedate):
                session.execute(sa.insert(DbWeather).values(db_item))

        return weather

    def process_anecdote_item(self, item: Anecdote):
        with open("anecdotes.txt", "w") as file:
            file.writelines(item.text)
        return item

    def process_wise_phrase_item(self, item: WisePhrase):
        with open("wise_phrases.txt", "w") as file:
            file.writelines(item.text)
        return item

    def is_new_value(self, session, city_id: int, datetime):
        exists = session.execute(sa.select(DbWeather).where(
            DbWeather.city_id == city_id,
            DbWeather.timedate == datetime
        )).fetchone()
        return False if exists else True