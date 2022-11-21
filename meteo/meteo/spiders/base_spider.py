from abc import ABC
from dataclasses import dataclass
from datetime import date
from typing import FrozenSet, List, Tuple

import arrow
from scrapy import Spider


@dataclass
class DateSpan:
    start: arrow.Arrow
    end: arrow.Arrow


class BaseSpider(Spider, ABC):
    date_range: DateSpan

    name: str
    allowed_domains: List[str]

    def __init__(
        self,
        dates: str = None,
        *args,
        **kwargs,
    ):
        if dates:
            #  -a dates=2022.01.01-2022.11.20
            dates = [arrow.get(x) for x in dates.split("-")]
            lookup_dates = DateSpan(start=min(dates), end=max(dates))
        else:
            # no date attribute
            tomorrow = arrow.get(arrow.now().date()).shift(days=1)
            lookup_dates = DateSpan(
                start=tomorrow,
                end=tomorrow,
            )
        self.logger.info(f"Scrape dates: from {lookup_dates.start.date()} to {lookup_dates.end.date()}")

        # data = {"sale_id": sale_id, "sale_number": sale_number}
        self.start_requests = lambda: self.crawl_calendar(
            dates=lookup_dates
        )

        super().__init__(*args, **kwargs)

    def crawl_calendar(self, *, dates: DateSpan):
        raise NotImplementedError()
