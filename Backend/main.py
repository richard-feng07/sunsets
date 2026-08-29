import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime, timedelta
from typing import Any, Optional
from flask import Flask
from flask_cors import CORS
import helpers
import payload_helpers as ph

app = Flask(__name__)
cors = CORS(app, origins="*")

load_dotenv(override=True)


class SunsetStructure:

    DESIRED: dict[str, float] = {
        "cloudCover": 30,
        "cloudBase": 3.5,
        "humidity": 45,
        "visibility": 10,
        "dewpoint" : 45,
        "windSpeed" : 8,
        "windGust" : 15
    }

    def __init__(self, url: Optional[str] = None, path: Optional[str] = None):
        if url is None and path is None:
            raise ValueError("Must provide either url or path")
        if url is not None and path is not None:
            raise ValueError("Provide only one of url or path")
        if url is not None:
            url += os.environ["API_KEY"]
            self.data = requests.get(url=url).json()
        else:
            with open(path, "r") as file:
                self.data = json.load(file)
        self.sunsets: dict[str, list[Any]] = {}

    def fill_sunset_times(self):
        for i in range(len(self.data["timelines"]["daily"])):
            today_sunset = self.data["timelines"]["daily"][i]["values"]["sunsetTime"]
            exact_sunset = (
                datetime.fromisoformat(today_sunset.replace("Z", "+00:00"))
                .astimezone()
                .strftime("%m/%d %I:%M %p")
            )
            hourly_sunset = (
                datetime.fromisoformat((today_sunset[0:14] + "00:00+00:00"))
                .astimezone()
                .strftime("%m/%d %I:%M %p")
            )
            self.sunsets[today_sunset] = [exact_sunset, hourly_sunset]

    def fill_weather(self):
        """
        For each sunset, find the hourly weather entry for the sunset hour
        and the hour after. Always append exactly 2 weather slots (which
        may be None if the hourly array doesn't have that time), so
        positional indices [2] and [3] are always safe to access.
        """
        for time in list(self.sunsets):
            sunset_hour_key = time[0:13] + ":00:00Z"
            dt = datetime.fromisoformat(time[0:13] + ":00:00+00:00")
            next_hour_key = (dt + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

            hour0 = None
            hour1 = None
            for weather in self.data["timelines"]["hourly"]:
                if weather["time"] == sunset_hour_key:
                    hour0 = weather
                elif weather["time"] == next_hour_key:
                    hour1 = weather

            self.sunsets[time].append(hour0)
            self.sunsets[time].append(hour1)

        if self.sunsets:
            self.sunsets.popitem()

    def get_forecast(self):
        good_sunsets: list[dict] = []
        for date in self.sunsets:
            entry = self.sunsets[date]

            if entry[2] is None or entry[3] is None:
                continue

            values_h0 = entry[2]["values"]
            values_h1 = entry[3]["values"]

            for cat in values_h0:
                if cat not in self.DESIRED:
                    continue

                v0 = values_h0.get(cat)
                v1 = values_h1.get(cat)

                if not isinstance(v0, (int, float)) or not isinstance(v1, (int, float)):
                    continue

                avg = helpers.get_sunset_time_average(
                    minutes=datetime.strptime(entry[0], "%m/%d %I:%M %p").minute,
                    category=cat,
                    sunsets=entry,
                )
                if helpers.relative_error(avg, self.DESIRED[cat]) < 0.8:
                    ph.check_payload_dupes(
                        good_sunsets,
                        {
                            entry[0]: [
                                {
                                    "category": cat,
                                    "real": v0,
                                    "desired": self.DESIRED[cat],
                                }
                            ]
                        },
                    )
            for i in range(len(good_sunsets)):
                date = next(iter(good_sunsets[i]))
                good_sunsets[i]['score'] = len(good_sunsets[i][date])
        return good_sunsets

    def get_sunsets(self):
        return self.sunsets

    def get_data(self):
        return self.data


url: str = (
    "https://api.tomorrow.io/v4/weather/forecast?location=irvine%20ca&units=imperial&apikey="
)

s = SunsetStructure(url=url)
s.fill_sunset_times()
s.fill_weather()
print(s.get_forecast())
# @app.route("/prediction", methods=["GET"])
# def prediction():
#     try:
#         s = SunsetStructure(url=url)
#         s.fill_sunset_times()
#         s.fill_weather()
#         return s.get_forecast()
#     except (KeyError, ValueError) as e:
#         return {"error": "unexpected response shape", "detail": str(e)}, 502

# if __name__ == "__main__":
#     app.run()