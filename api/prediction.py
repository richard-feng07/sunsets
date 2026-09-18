import os
import sys
from dotenv import load_dotenv
import requests
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from tzfpy import get_tz
from typing import Any, Optional
from flask import Flask, request
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import _helpers as helpers
from urllib.parse import quote

app = Flask(__name__)

load_dotenv(override=True)

MOCK_FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_testing.json")


class SunsetStructure:

    DESIRED: dict[str, float] = {
        "cloudCover": 30,
        "humidity": 45,
        "visibility": 9,
        "dewPoint" : 45,
        "windSpeed" : 8,
        "windGust" : 15
    }

    UNITS: dict[str, str] = {
    "cloudCover": "%", "humidity": "%",
    "visibility": "mi", "dewPoint": "°F", "windSpeed": "mph", "windGust": "mph",
    }

    LABELS: dict[str, str] = {
        "cloudCover": "cloud cover", "humidity": "humidity",
        "visibility": "visibility", "dewPoint": "dew point",
        "windSpeed": "wind speed", "windGust": "wind gust",
    }


    def __init__(self, url: Optional[str] = None, path: Optional[str] = None, query: str = ""):
        if url is None and path is None:
            raise ValueError("Must provide either url or path")
        if url is not None and path is not None:
            raise ValueError("Provide only one of url or path")
        if url is not None:
            url += os.environ["API_KEY"]
            response = requests.get(url=url, timeout=20)
            self.data = response.json()
            if not response.ok:
                raise ValueError(
                    self.data.get("message") or "the forecast service rejected that location"
                )
        else:
            with open(path, "r") as file:
                self.data = json.load(file)
        lat = self.data["location"]["lat"]
        lon = self.data["location"]["lon"]
        self.location = helpers.format_place(self.data["location"].get("name"), query)
        self.tz = ZoneInfo(get_tz(lon, lat))
        self.sunsets: dict[str, list[Any]] = {}
        self.forecast = []
        self.threshold = 0.3

    def fill_sunset_times(self):
        for i in range(len(self.data["timelines"]["daily"])):
            today_sunset = self.data["timelines"]["daily"][i]["values"]["sunsetTime"]
            dt_local = (
                datetime.fromisoformat(today_sunset.replace("Z", "+00:00"))
                .astimezone(self.tz)
            )
            exact_sunset = dt_local.strftime("%-m/%-d %-I:%M %p")
            hourly_sunset = (
                datetime.fromisoformat((today_sunset[0:14] + "00:00+00:00"))
                .astimezone(self.tz)
                .strftime("%-m/%-d %-I:%M %p")
            )
            self.sunsets[today_sunset] = [exact_sunset, hourly_sunset, dt_local]

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
        self.forecast = []
        for date in self.sunsets:
            self.forecast.append({
                "timestamp" : date,
                "label" : self.sunsets[date][0],
                "score" : 0,
                "readings" : []
            })
        for date in self.sunsets:
            entry = self.sunsets[date]
            current = next(f for f in self.forecast if f["timestamp"] == date)
            if entry[3] is None or entry[4] is None:
                continue

            values_h0 = entry[3]["values"]
            values_h1 = entry[4]["values"]

            for cat in values_h0:
                if cat not in self.DESIRED:
                    continue

                v0 = values_h0.get(cat)
                v1 = values_h1.get(cat)

                if not isinstance(v0, (int, float)) or not isinstance(v1, (int, float)):
                    continue

                avg = helpers.get_sunset_time_average(
                    minutes=entry[2].minute,
                    category=cat,
                    sunsets=entry,
                )
                current['readings'].append({
                    "category" : cat,
                    "label" : self.LABELS[cat],
                    "real" : round(avg, 1),
                    "desired" : self.DESIRED[cat],
                    "unit" : self.UNITS[cat],
                    "met" : helpers.relative_error(avg, self.DESIRED[cat]) < self.threshold
                })
            current["score"] = sum(r["met"] for r in current["readings"])
        return {"place" : self.location, "data" : self.forecast}

    def get_sunsets(self):
        return self.sunsets

    def get_data(self):
        return self.data

@app.route("/api/prediction", methods=["GET"])
@app.route("/prediction", methods=["GET"])
def prediction():
    location = request.args.get("location", "").strip()
    if not location:
        return {"error": "Please enter a valid location"}, 400
    try:
        if location == "mock":
            s = SunsetStructure(path=MOCK_FIXTURE, query="Irvine, California")
        else:
            api_url = (
                "https://api.tomorrow.io/v4/weather/forecast"
                f"?location={quote(location)}&units=imperial&apikey="
            )
            s = SunsetStructure(url=api_url, query=location)
        s.fill_sunset_times()
        s.fill_weather()
        return s.get_forecast()
    except ValueError as e:
        return {"error": str(e)}, 502
    except (KeyError, FileNotFoundError, requests.RequestException) as e:
        return {"error": "unexpected response shape", "detail": str(e)}, 502

if __name__ == "__main__":
    app.run()