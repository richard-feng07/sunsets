import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
from typing import Any


load_dotenv(override=True)

# url='https://api.tomorrow.io/v4/weather/forecast?location=42.3478,-71.0466&units=imperial&apikey=' + os.environ['API_KEY']
# data = requests.get(url=url).json()
sunsets: dict[str, list[Any]] = {}
sweet_spot = {
    "cloudCover": 50,
    "cloudBase": 0.568,
    "humidity": 0.15,
    "precipitationProbability": 0.1
}
with open('src/testing.json', 'r') as file:
    data = json.load(file)
for i in range(len(data['timelines']['daily'])):
    today_sunset = data['timelines']['daily'][i]['values']['sunsetTime']
    exact_sunset = datetime.fromisoformat(
        today_sunset.replace('Z', '+00:00')).astimezone()
    hourly_sunset = datetime.fromisoformat(
        (today_sunset[0:14] + "00:00+00:00")).astimezone()
    sunsets[today_sunset] = [exact_sunset, hourly_sunset]

# for dates in sunsets:
#     print(f'{sunsets[dates][0].strftime("%I:%M %p")} on {sunsets[dates][0].strftime("%m/%d")}')
    # print("Hourly sunset: " + sunsets[i][0].strftime("%I:%M %p"))


for weather in data['timelines']['hourly']:
    if weather['time'] == today_sunset[0:13] + ":00:00Z":
        sunset_stats = weather

for time in sunsets:
    for weather in data['timelines']['hourly']:
        if (weather['time'] == time[0:13] + ":00:00Z"):
            sunsets[time].append(weather)

# print(f"Here are the current weather stats at that time: {sunset_stats}")


def relative_error(this, target):
    try:
        return abs(this - target) / target
    except ZeroDivisionError:
        raise ZeroDivisionError("Can't have target value be 0")

# for cat in sunset_stats['values']:
#     if(isinstance(sunset_stats['values'][cat], int) or isinstance(sunset_stats['values'][cat], float)):
#         try:
#             if(relative_error(sunset_stats['values'][cat], sweet_spot[cat]) < 0.15):
#                 print(cat)
#         except KeyError:
#             pass


sunsets.popitem()

for date in sunsets:
    for cat in sunsets[date][2]['values']:
        if (isinstance(sunsets[date][2]['values'][cat], int) or isinstance(
                sunsets[date][2]['values'][cat], float)):
            try:
                if (relative_error(
                        sunsets[date][2]['values'][cat], sweet_spot[cat]) < 0.15):
                    print(
                        f'There may be a good sunset on {sunsets[date][0].strftime("%m/%d")} at {sunsets[date][0].strftime("%I:%M %p")} because of good {cat}')
            except KeyError:
                pass
