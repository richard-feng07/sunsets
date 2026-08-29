from main import SunsetStructure
from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
cors = CORS(app, origins="*")

url: str = (
    "https://api.tomorrow.io/v4/weather/forecast?location=41.4901,-71.3128&units=imperial&apikey="
)

@app.route("/prediction", methods=["GET"])
def prediction():
    try:
        s = SunsetStructure(url=url)
        s.fill_sunset_times()
        s.fill_weather()
        return s.get_forecast()
    except (KeyError, ValueError) as e:
        return {"error": "unexpected response shape", "detail": str(e)}, 502

if __name__ == "__main__":
    app.run()