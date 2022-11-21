import datetime
import re
from typing import List

import scrapy
from arrow import Arrow
from yarl import URL

from .base_spider import BaseSpider, DateSpan
from ..items.anecdote import Anecdote
from ..items.enums import WindDirection
from ..items.weather import Span, Weather
from ..items.wise_phrase import WisePhrase


class MeteoBySpider(BaseSpider):
    name = "meteo_by"
    allowed_domains = ["meteo.by"]
    meteo_by = URL("https://meteo.by/")
    city: str = None
    # typical URL here is https://meteo.by/vitebsk/retro/2022-11-20/
    # this is the shift in time
    # not precise at all, and mostly empirical
    time_mapping = {
        "ночь": 2,
        "утро": 8,
        "день": 14,
        "вечер": 20,
    }

    wind_direction_mapping = {
        "с": WindDirection.NORTH,
        "ю": WindDirection.SOUTH,
        "з": WindDirection.WEST,
        "в": WindDirection.EAST,
        "с-з": WindDirection.NORTH_WEST,
        "с-в": WindDirection.NORTH_EAST,
        "ю-з": WindDirection.SOUTH_WEST,
        "ю-в": WindDirection.SOUTH_EAST,
    }
    by_tz = datetime.timezone(datetime.timedelta(hours=-3))

    # coordinates_mapping = {
    #     "baranavichy": (53.1159, 25.9912),
    #     "bobruysk": (53.1159, 25.9912),
    #     "borisov": (54.2528, 28.4566),
    #     "brest": (52.1267, 23.6666),
    #     "vitebsk": (55.1771, 30.2217),
    #     "gomel": (52.4351, 31.0549),
    #     "grodno": (53.6603, 23.8166),
    #     "lida": (53.8809, 25.3029),
    #     "minsk": (53.8533, 27.8503),
    #     "mogilev": (53.9102, 30.3501),
    #     "mozyr": (52.0434, 29.2332),
    #     "orsha": (54.509167, 30.425833),
    #     "pinsk": (52.1101, 26.0833),
    #     "polotsk": (55.4773, 28.8),
    #     "slutsk": (53.0102, 27.5499),
    #     "salihorsk": (52.7984, 27.5407),
    # }

    @staticmethod
    def generate_dates(dates: DateSpan) -> List[Arrow]:
        res = [dates.start]
        next_day = dates.start.shift(days=1)
        while not next_day >= dates.end:
            res.append(next_day)
            next_day = next_day.shift(days=1)
        return res

    @staticmethod
    def split_into_span(string_values: str) -> Span:
        vals = [int(x) for x in string_values.split("…")]
        return Span(vals)

    def locate_temp(self, values: list) -> Span:
        res = list()
        for line in values:
            found = re.findall(r"[\+-]\d+?|0", line)
            [res.append(int(x)) for x in found]
        return Span(res)

    def parse(self, **kwargs):
        raise "You shall not pass!"  # TODO a script should not appear here

    def crawl_calendar(self, dates: DateSpan):
        if not self.city:
            raise ValueError("meteo_by spider requires a city: -a city=minsk")
        dates_pack = self.generate_dates(dates)
        for date in dates_pack:
            yield scrapy.Request(
                url=str(self.meteo_by / self.city / "retro" / str(date.date())),
                callback=self.parse_single_day,
                cb_kwargs={"date": date},
            )

    def parse_single_day(self, response, date: Arrow):
        weather_rows = response.xpath(
            "//table[contains(@class,'t-weather')]//tr[contains(@class, 'time')]"
        )
        for row in weather_rows:
            temp_raw = row.xpath("./td[contains(@class, 'temp')]//text()").getall()
            self.locate_temp(temp_raw)
            time_raw = row.xpath("./td[contains(@class, 'temp')]/text()").get()
            weather_type_raw = row.xpath(
                "./td[contains(@class, 'icon')]/text()[2]"
            ).get()
            data_chunk = row.xpath("./td[contains(@class, 'data')]/text()").getall()
            pressure_raw, humidity_raw, wind_speed_raw = data_chunk
            wind_direction_raw = (
                row.xpath("./td[contains(@class, 'dir')]/text()").get().strip()
            )
            time = self.time_mapping[time_raw]
            weather_item = Weather(
                timedate=date.shift(hours=time).astimezone(self.by_tz),
                weather_type_raw=weather_type_raw.strip(),
                city_name=self.city,
                atm_pressure=self.split_into_span(pressure_raw),
                humidity=self.split_into_span(humidity_raw),
                wind_speed=self.split_into_span(wind_speed_raw),
                wind_direction=self.wind_direction_mapping[wind_direction_raw],
                temp=self.locate_temp(temp_raw),
            )
            yield weather_item

        anecdote_raw = response.xpath(
            "//div[contains(@class, 'fun-i')]/p/text()"
        ).getall()
        yield Anecdote(text="\n".join(anecdote_raw))
        wise_phrase_raw = response.xpath(
            "//div[contains(@class, 'aphorism-i')]/p/text()"
        ).getall()
        yield WisePhrase(text="\n".join(wise_phrase_raw))
