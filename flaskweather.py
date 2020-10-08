# flasknewsreader.py
# Version: <see below>
# Author : Jochen Peters

from flask import Flask, Blueprint, render_template, request, redirect
import requests
import json
from datetime import datetime, timezone, timedelta


# Parameters and settings
VERSION_INFO = {
	'version_number': '0.9',
	'version_date': '2020-10-08'
}
LOCATIONS_FILENAME = 'locations.json'
OWM_API_URL = 'https://api.openweathermap.org/data/2.5/onecall'
OWM_ICON_URL = 'http://openweathermap.org/img/wn/'
OWM_API_KEY = '123abc' # TODO: remove key before git commit(!)


# Global variables
fw_bp = Blueprint('flaskweather', __name__, template_folder='templates', static_folder='static', static_url_path='/weather/static')


# General functions

def load_locations():
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

def fetch_weather_data(lat, lon):
	url = OWM_API_URL + '?units=metric&lat=' + str(lat) + '&lon=' + str(lon) + '&appid=' + OWM_API_KEY
	response = requests.get(url)
	if response.ok:
		return response.json()
	else:
		return None

def load_test_weather_data(filename): # for TESTING
	with open(filename, mode='r') as f:
		dictionary = json.load(f)
	return dictionary


# Routes

@fw_bp.route('/weather')
def weather():
	locations = load_locations()
	loc_idx = sanitize_location_idx(locations, request.args.get('loc'))
	if loc_idx is None:
		return redirect('/weather?loc=0')

	weather_data = fetch_weather_data(locations[loc_idx]['lat'], locations[loc_idx]['lon'])
	weather_data['updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	weather_data['location_name'] = locations[loc_idx]['name']

	return render_template('weather.html', locations=locations, weather_data=weather_data)


# Template filters

@fw_bp.app_template_filter('filter_dt')
def filter_dt(dt, offset, format_string):
	return datetime.fromtimestamp(dt, tz=timezone(timedelta(seconds=offset))).strftime(format_string)
