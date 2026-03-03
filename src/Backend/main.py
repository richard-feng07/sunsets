import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
from typing import Any, Optional
from flask import Flask, jsonify
from flask_cors import CORS
import helpers
from datetime import timedelta, datetime

app = Flask(__name__)
cors = CORS(app, origins="*")

load_dotenv(override=True)

# malibu
# url='https://api.tomorrow.io/v4/weather/forecast?location=34.0406,-118.8396&units=imperial&apikey=' + os.environ['API_KEY']

# url = 'https://api.tomorrow.io/v4/weather/forecast?location=42.3478,-71.0466&units=imperial&apikey=' + \
#     os.environ['API_KEY']
# print(url)
# data = requests.get(url=url).json()


class SunsetStructure:

    sweet_spot: dict[str, float] = {
        "cloudCover": 50,
        "cloudBase": 0.40,
        "humidity": 45,
    }

    def __init__(self, url: Optional[str] = None, path: Optional[str] = None):
        if (url is None and path is None):
            raise ValueError
        if (url is not None and path is not None):
            raise ValueError
        if (url is not None):
            self.data = requests.get(url=url).json()
        else:
            with open('src/testing.json', 'r') as file:
                self.data = json.load(file)
        self.sunsets: dict[str, list[Any]] = {}

    def fill_sunset_times(self):
        for i in range(len(self.data['timelines']['daily'])):
            today_sunset = self.data['timelines']['daily'][i]['values']['sunsetTime']
            exact_sunset = datetime.fromisoformat(
                today_sunset.replace('Z', '+00:00')).astimezone().strftime("%m/%d %I:%M %p")
            hourly_sunset = datetime.fromisoformat(
                (today_sunset[0:14] + "00:00+00:00")).astimezone().strftime("%m/%d %I:%M %p")
            self.sunsets[today_sunset] = [exact_sunset, hourly_sunset]

    def fill_weather(self):
        for time in self.sunsets:
            for weather in self.data['timelines']['hourly']:
                dt = datetime.fromisoformat(time[0:13] + ":00:00+00:00")
                new = (str(dt + timedelta(hours=1)).replace(" ", "T")
                       )[0:20].replace("+", "Z")
                if (weather['time'] == time[0:13] + ":00:00Z" or
                            weather['time'] == new
                        ):
                    self.sunsets[time].append(weather)
        self.sunsets.popitem()

    def updated_forecast(self):
        good_sunsets: list[dict] = []
        for date in self.sunsets:
            if (len(self.sunsets[date]) < 3):
                continue
            for cat in self.sunsets[date][2]['values']:
                if (cat in self.sweet_spot and (isinstance(self.sunsets[date][2]['values'][cat], float) or isinstance(self.sunsets[date][2]['values'][cat], int))):
                    if (helpers.relative_error(helpers.get_sunset_time_average(
                        minutes=datetime.strptime(
                            self.sunsets[date][0], '%m/%d %I:%M %p').minute,
                        category=cat,
                        sunsets=self.sunsets[date]
                    ), self.sweet_spot[cat] < 0.9)):
                        good_sunsets.append(
                            {self.sunsets[date][0]: {'category': cat, 'real': self.sunsets[date][2]['values'][cat], 'desired': self.sweet_spot[cat]}})
        return good_sunsets

    def get_forecast(self):
        good_sunsets: list[dict] = []
        count = -1
        for date in self.sunsets:
            if (len(self.sunsets[date]) < 3 or self.sunsets[date][2] is None):
                continue
            for cat in self.sunsets[date][2]['values']:
                if (isinstance(self.sunsets[date][2]['values'][cat], int) or isinstance(
                        self.sunsets[date][2]['values'][cat], float)):
                    try:
                        if (helpers.relative_error(
                                self.sunsets[date][2]['values'][cat], self.sweet_spot[cat]) < 0.3):
                            print(self.sunsets[date][0])
                            if any(self.sunsets[date][0].strftime("%m/%d %I:%M %p") in k for k in good_sunsets):
                                good_sunsets[count][self.sunsets[date][0].strftime("%m/%d %I:%M %p")].append(
                                    {cat: {"real": self.sunsets[date][2]['values'][cat], "desired": self.sweet_spot[cat]}})
                            else:
                                count += 1
                                print(self.sunsets[date][0])
                                good_sunsets.append(
                                    {self.sunsets[date][0].strftime("%m/%d %I:%M %p"): []})
                                good_sunsets[count][self.sunsets[date][0].strftime("%m/%d %I:%M %p")].append(
                                    {cat: {"real": self.sunsets[date][2]['values'][cat], "desired": self.sweet_spot[cat]}})
                    except KeyError:
                        pass
        return good_sunsets

    def get_sunsets(self):
        return self.sunsets

    def get_data(self):
        return self.data


s = SunsetStructure(path='src/testing.json')
s.fill_sunset_times()
s.fill_weather()
print(s.updated_forecast())


@app.route("/prediction", methods=['GET'])
def prediction():
    s = SunsetStructure(path='src/testing.json')
    s.fill_exact_sunsets()
    s.fill_weather()
    return s.get_forecast()


# print(prediction())


# if __name__ == "__main__":
#     app.run(port=8000, debug=True)
