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
                elif column_name == "city_id":
                    value = city_id.id
                else:
                    value = getattr(weather, column_name)
                db_item[column_to_fill] = value

            if not self.is_weather_entry_exists(session=session, city_id=city_id.id, datetime=weather.timedate):
                session.execute(sa.insert(DbWeather).values(db_item))
                session.commit()

        return weather

    @staticmethod
    def process_anecdote_item(item: Anecdote):
        with open("anecdotes.txt", "a+") as file:
            file.writelines(item.text)
            file.writelines("\n")
            file.writelines("\n")

        return item

    @staticmethod
    def process_wise_phrase_item(item: WisePhrase):
        with open("wise_phrases.txt", "a+") as file:
            file.writelines(item.text)
            file.writelines("\n")
            file.writelines("\n")
        return item

    @staticmethod
    def is_weather_entry_exists(session, city_id: int, datetime):
        exists = session.execute(sa.select(DbWeather).where(
            DbWeather.city_id == city_id,
            DbWeather.timedate == datetime
        )).fetchone()
        return True if exists else False
