# flasknewsreader.py
# Version: <see below>
# Author : Jochen Peters

from flask import Flask, Blueprint, render_template, request, redirect
from datetime import datetime, timezone, timedelta
import requests
import json
import os
from lib.dotenv import load_dotenv


# Parameters and settings
VERSION_INFO = {
	'version_number': '0.9.6',
	'version_date': '2025-01-25'
}
DOTENV_FILENAME = '.env'
LOCATIONS_FILENAME = 'locations.json'
OWM_API_URL = {}
OWM_API_URL['WEATHER'] = 'https://api.openweathermap.org/data/2.5/weather'
OWM_API_URL['FORECAST'] = 'https://api.openweathermap.org/data/2.5/forecast'
OWM_ICON_URL = 'http://openweathermap.org/img/wn/'


# Global variables
fw_bp = Blueprint('flaskweather', __name__, template_folder='templates', static_folder='static', static_url_path='/weather/static')


# General functions

def load_locations():
	global LOCATIONS_FILENAME
	this_folder = os.path.dirname(os.path.abspath(__file__))
	LOCATIONS_FILENAME = os.path.join(this_folder, LOCATIONS_FILENAME)
	dictionary = None
	with open(LOCATIONS_FILENAME, mode='r') as f:
		dictionary = json.load(f)
	return dictionary

def sanitize_location_idx(locations, idx):
	if locations is None:
		return None

	try:
		loc_idx = int(idx)
	except:
		return None

	if loc_idx < 0 or loc_idx >= len(locations):
		return None

	return loc_idx

def fetch_weather_data(api, lat, lon):
	if not api in OWM_API_URL:
		return None
	url = OWM_API_URL[api] + '?units=metric&lat=' + str(lat) + '&lon=' + str(lon) + '&appid=' + os.environ['OWM_API_KEY']
	response = requests.get(url)
	if response.ok:
		return response.json()
	else:
		return None

def get_precip_sum(api_data, fieldname):
	# current weather API: fieldname="1h", forecast API fieldname="3h"
	precip_sum = 0
	for precip_type in ["rain", "snow"]:
		if (precip_type in api_data) and (fieldname in api_data[precip_type]):
			precip_sum += api_data[precip_type][fieldname]
	return precip_sum

def get_precip_class(api_data):
	# list of condition codes here: https://openweathermap.org/weather-conditions
	precip_class = ""
	if "pop" in api_data:
		if api_data["pop"] >= 0.5:
			if api_data["weather"][0]["id"] in [200, 230, 231, 300, 301, 310, 311, 500, 520, 612, 615]:
				precip_class = "light_rain"
			elif api_data["weather"][0]["id"] in [201, 202, 232, 302, 312, 313, 314, 321, 501, 502, 503, 504, 511, 521, 522, 531, 611, 613, 616]:
				precip_class = "rain"
			elif api_data["weather"][0]["id"] in [600, 620]:
				precip_class = "light_snow"
			elif api_data["weather"][0]["id"] in [601, 602, 621, 622]:
				precip_class = "snow"
	return precip_class

def check_high_gusts(api_data):
	if "gust" in api_data["wind"]:
		return api_data["wind"]["gust"] - api_data["wind"]["speed"] > 5
	else:
		return False

def load_test_weather_data(filename): # for TESTING
	with open(filename, mode='r') as f:
		dictionary = json.load(f)
	return dictionary


# Routes

@fw_bp.route('/weather')
def weather():
	# read local files
	global DOTENV_FILENAME
	this_folder = os.path.dirname(os.path.abspath(__file__))
	DOTENV_FILENAME = os.path.join(this_folder, DOTENV_FILENAME)
	load_dotenv(DOTENV_FILENAME)
	locations = load_locations()
	if locations is None:
		return "no locations"
	loc_idx = sanitize_location_idx(locations, request.args.get('loc'))
	if loc_idx is None:
		return redirect('/weather?loc=0')

	# fetch weather data
	data_current = fetch_weather_data('WEATHER', locations[loc_idx]['lat'], locations[loc_idx]['lon'])
	if data_current is None:
		return "no weather data"
	data_forecast = fetch_weather_data('FORECAST', locations[loc_idx]['lat'], locations[loc_idx]['lon'])
	if data_forecast is None:
		return "no forecast data"

	# add-up precipitation and set precip class
	data_current["fw_precip_sum"] = get_precip_sum(data_current, "1h")
	data_current["fw_show_gust"] = check_high_gusts(data_current)
	for fcdat in data_forecast["list"]:
		fcdat["fw_precip_sum"] = get_precip_sum(fcdat, "3h")
		fcdat["fw_precip_class"] = get_precip_class(fcdat)
		fcdat["fw_show_gust"] = check_high_gusts(fcdat)

	# assemble weather data to pass to template
	weather_data = {
		'location_name': locations[loc_idx]['name'],
		'updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
		'current': data_current,
		'forecast': data_forecast
	}
	#return weather_data # DEBUG
	return render_template('weather.html', locations=locations, weather_data=weather_data)


# Template filters

@fw_bp.app_template_filter('filter_dt')
def filter_dt(dt, offset, format_string):
	return datetime.fromtimestamp(dt, tz=timezone(timedelta(seconds=offset))).strftime(format_string)
