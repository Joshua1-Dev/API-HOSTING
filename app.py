from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import os

app = Flask(__name__)

CORS(app, supports_credentials=True)

access_token = os.getenv(Ipinfo_key)
api_key = os.getenv(API_KEY)
if api_key is None:
    raise EnvironmentError('API_KEY environment variable')


# Endpoint to handle GET requests
@app.route('/api/hello', methods=['GET'])
def hello():

    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    else:
        client_ip = request.remote_addr
    visitor_name = request.args.get("visitor_name", default='Guest', type=str)

    url = f"https://ipinfo.io/{client_ip}/json"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        location = data.get("city", "unknown location")

        def get_weather(loc, key):
            base_url = "https://api.weatherapi.com/v1/current.json"
            params = {
                "key": key,
                "q": loc,
                "aqi": "no"  # Optional: Include this parameter to disable Air Quality Index (AQI) data
            }
            response = requests.get(base_url, params=params)
            if response:
                return response.json()
            else:
                print(f"Error: Unable to fetch weather data for {location}")
                return None
        weather_data = get_weather(location, api_key)
        if weather_data:
            temp = weather_data["current"]["temp_c"]

            # Simulate fetching temperature (this would typically come from a weather API)
            temperature = temp # Example temperature

            # Prepare response
            greeting = f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {location}"
            response = {
                "client_ip": client_ip,
                "location": location,
                "greeting": greeting
            }

        return jsonify(response)


@app.route("/")
def index():
    return jsonify({
        "Message": "Welcome to Home Page"
    })


if __name__ == '__main__':
    app.run(debug=True)
