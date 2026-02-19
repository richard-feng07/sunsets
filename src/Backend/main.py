import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
from typing import Any
from flask import Flask, jsonify
import helpers

app = Flask(__name__)

load_dotenv(override=True)
# malibu
# url='https://api.tomorrow.io/v4/weather/forecast?location=34.0406,-118.8396&units=imperial&apikey=' + os.environ['API_KEY']

# url='https://api.tomorrow.io/v4/weather/forecast?location=42.3478,-71.0466&units=imperial&apikey=' + os.environ['API_KEY']
# print(url)
# data = requests.get(url=url).json()
with open('src/testing.json', 'r') as file:
    data = json.load(file)
sunsets: dict[str, list[Any]] = {}
sweet_spot = {
    "cloudCover": 50,
    "cloudBase": 0.40,
    "humidity": 45,
    "precipitationProbability": 0.1
}

for i in range(len(data['timelines']['daily'])):
    today_sunset = data['timelines']['daily'][i]['values']['sunsetTime']
    exact_sunset = datetime.fromisoformat(
        today_sunset.replace('Z', '+00:00')).astimezone()
    hourly_sunset = datetime.fromisoformat(
        (today_sunset[0:14] + "00:00+00:00")).astimezone()
    sunsets[today_sunset] = [exact_sunset, hourly_sunset]

for weather in data['timelines']['hourly']:
    if weather['time'] == today_sunset[0:13] + ":00:00Z":
        sunset_stats = weather

for time in sunsets:
    for weather in data['timelines']['hourly']:
        if (weather['time'] == time[0:13] + ":00:00Z"):
            sunsets[time].append(weather)


sunsets.popitem()


@app.route("/forecast")
def get_forecast():
    good_sunsets: list[dict] = []
    count = -1
    for date in sunsets:
        for cat in sunsets[date][2]['values']:
            if (isinstance(sunsets[date][2]['values'][cat], int) or isinstance(
                    sunsets[date][2]['values'][cat], float)):
                try:
                    if (helpers.relative_error(
                            sunsets[date][2]['values'][cat], sweet_spot[cat]) < 0.9):
                        if any(sunsets[date][0].strftime("%m/%d %I:%M %p") in k for k in good_sunsets):
                            good_sunsets[count][sunsets[date][0].strftime("%m/%d %I:%M %p")].append(
                                {cat: {"real": sunsets[date][2]['values'][cat], "desired": sweet_spot[cat]}})
                        else:
                            count += 1
                            good_sunsets.append(
                                {sunsets[date][0].strftime("%m/%d %I:%M %p"): []})
                            good_sunsets[count][sunsets[date][0].strftime("%m/%d %I:%M %p")].append(
                                {cat: {"real": sunsets[date][2]['values'][cat], "desired": sweet_spot[cat]}})
                except KeyError:
                    pass
    return good_sunsets


print(get_forecast())

# if __name__ == "__main__":
#     app.run(port=8000, debug=True)
