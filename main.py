import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json
import db
import sqlite3
import plotly
import plotly.graph_objs as go
from tabulate import tabulate
import datetime
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.express as px


BASE_URL = 'https://www.wsdot.com'
# added forward slash for crawling purposes
CAMERA_PATH = '/Traffic/routelist.aspx'
WEATHER_PATH = '/traffic/weather/default.aspx'
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}

headers = {
	'User-Agent': 'UMSI 507 Course Final Project - Scraping & Database',
	'From': 'lanxuanz@umich.edu', 
	'Course-Info': 'https://si.umich.edu/programs/courses/507'
}



def load_cache():
	try:
		cache_file = open(CACHE_FILE_NAME, 'r')
		cache_file_contents = cache_file.read()
		cache = json.loads(cache_file_contents)
		cache_file.close()
	except:
		cache = {}
	return cache


def save_cache(cache):
	cache_file = open(CACHE_FILE_NAME, 'w')
	contents_to_write = json.dumps(cache)
	cache_file.write(contents_to_write)
	cache_file.close()


def make_url_request_using_cache(url, cache):
	if (url in cache.keys()): # the url is our unique key
		print("Using cache")
		return cache[url]
	else:
		print("Fetching")
		time.sleep(1)
		response = requests.get(url, headers=headers)
		cache[url] = response.text # notice that we save response.text to our cache dictionary. We turn it into a BeautifulSoup object later, since BeautifulSoup objects are nor json parsable. 
		save_cache(cache)
		return cache[url] # in both cases, we return cache[url]


## Load the cache, save in global variable
CACHE_DICT = load_cache()



# ## Make the soup for the Courses page
# camera_page_url = BASE_URL + CAMERA_PATH
# url_text = make_url_request_using_cache(camera_page_url, CACHE_DICT)
# soup = BeautifulSoup(url_text, 'html.parser') # convert our saved cache data to a BeautifulSoup object




# ## For each camera listed
# route_list = soup.find_all('table', class_="RouteList")
# # camera_listing_trs = camera_listing_parent.find_all('tr', recursive=False)


# for route in route_list:
# 	main_route = route.find_all('tr', class_="roadListDescr")


# 	for camera in main_route:
# 		camera_link_tag = camera.find_all('a')

# 		for single_camera in camera_link_tag:

# 			print(single_camera.text) #I-5 at MP 0.32: Interstate Bridge
# 			# print(single_camera) #<a href="https://images.wsdot.wa.gov/nw/525vc00 ... </a>

# 			print('----------------------------')
# 		print('another cameraal|||||||||||||||||||||||||||||||||||||||||||||')
# 		# camera_details_url = camera_link_tag['href']

# 		# ## Make the soup for camera details
# 		# url_text = make_url_request_using_cache(camera_details_url, CACHE_DICT)
# 		# soup = BeautifulSoup(url_text, 'html.parser')

# 		# print(soup)

DB_NAME = 'WSDOT.sqlite'

db.create_db()


weather_page_url = BASE_URL + WEATHER_PATH
url_text = make_url_request_using_cache(weather_page_url, CACHE_DICT)
soup = BeautifulSoup(url_text, 'html.parser') # convert our saved cache data to a BeautifulSoup object


zone_list = soup.find_all('div', class_="forecastZone")
n=0
for zone in zone_list:
	zone_link_tag = zone.find('a')
	zone_link = zone_link_tag['href']
	base_weather_url='https://www.wsdot.com/traffic/weather/'
	zone_url =base_weather_url+ zone_link
	
	response = requests.get(zone_url)
	soup = BeautifulSoup(response.text, 'html.parser')

	weather_detail_list = soup.find_all('a',class_="templink")


	for weather_detail_tag in weather_detail_list:
		weather_detail_link = weather_detail_tag['href']
		weather_detail_url = base_weather_url + weather_detail_link

		response = requests.get(weather_detail_url)
		soup = BeautifulSoup(response.text, 'html.parser')

		location = soup.find(class_='widget border').find(class_='greyBg').text.strip()
		AirTemperature = soup.find(id='AirTemperature').text.strip()
		if AirTemperature == 'N/A':
			AirTemperature = None
		else:
			AirTemperature = AirTemperature[:2]
		HighLow24Hour = soup.find(id='HighLow24Hour').text.strip()
		if HighLow24Hour == 'N/A':
			HighLow24Hour = None
		# Pressure = soup.find(id='Pressure').text.strip()
		# Elevation = soup.find(id='Elevation').text.strip()
		Humidity = soup.find(id='Humidity').text.strip()
		if Humidity == 'N/A':
			Humidity = None
		Visibility = soup.find(id='Visibility').text.strip()
		if Visibility == 'N/A':
			Visibility = None
		else:
			Visibility = Visibility[:1]
		# DewPoint = soup.find(id='DewPoint').text.strip()
		WindSpeed = soup.find(id='WindSpeed').text.strip()
		if WindSpeed == 'N/A':
			WindSpeed = None
		else:
			WindSpeed = WindSpeed[:1]
		# WindDirection = soup.find(id='WindDirection').text.strip()
		recent_weather_link = soup.find(class_='descriplink')

		# print(location)


		recent_weather_url = BASE_URL + recent_weather_link['href']
		response = requests.get(recent_weather_url)
		soup = BeautifulSoup(response.text, 'html.parser')

		temp = soup.find_all('tr')
		for item in temp[1:7]:
			aa = item.text.strip()
			aa = aa.split()
			date_time = aa[0]
			point_temperature = aa[1]
			if point_temperature == 'NA':
				point_temperature = None
			point_humidity = aa[3]
			if point_humidity == 'NA':
				point_humidity = None
			point_wind_speed = aa[6]
			if point_wind_speed == 'NA':
				point_wind_speed = None

			# print(point_wind_speed)


			insert_weather_sql = '''
				INSERT INTO weather
				VALUES (NULL, ?, ?, ?, ?, ?, ?, ?,?,?,?)
				'''
			conn = sqlite3.connect(DB_NAME)
			cur = conn.cursor()
			
			cur.execute(insert_weather_sql,
				[
					location,
					AirTemperature,
					HighLow24Hour, 
					Humidity,
					Visibility,
					WindSpeed,
					date_time,
					point_temperature,
					point_humidity,
					point_wind_speed
				])
				
			conn.commit()
			conn.close()




	# weather_map_detail = soup.find_all('area',shape="rect")
	# for map_tag in weather_map_detail:
	# 	map_tag_link = map_tag['href']
	# 	map_tag_url = base_weather_url + map_tag_link
	
	# 	response = requests.get(map_tag_url)
	# 	soup = BeautifulSoup(response.text, 'html.parser')


	# 	weather_detail_list = soup.find_all('a',class_="seltemplink")
	# 	for weather_detail_tag in weather_detail_list:
	# 		weather_detail_link = weather_detail_tag['href']
	# 		weather_detail_url = base_weather_url + weather_detail_link
			
	# 		response = requests.get(weather_detail_url)
	# 		soup = BeautifulSoup(response.text, 'html.parser')

	# 		number_name = soup.find_all(class_='weatherLabelsLeft')


	# 	weather_detail_list2 = soup.find_all('a',class_="templink")

	# 	for weather_detail_tag in weather_detail_list2:
	# 		weather_detail_link = weather_detail_tag['href']
	# 		weather_detail_url = base_weather_url + weather_detail_link


print('database ready')


def weather_table_info(location):

	query = 'SELECT * FROM weather \
	WHERE location = \'{}\' '.format(location)

	connection = sqlite3.connect(DB_NAME)
	cursor = connection.cursor()
	result = cursor.execute(query).fetchall()
	connection.close()


	latest_weather_result = list(result[0])
	data = [latest_weather_result[1:7]]
	headers=['Location', 'Air Temperature\n (F)', 'High & Low 24 Hour\n (f)', 'Humidity\n (%)','Visibility\n (mile)','WindSpeed\n (mph)']
	print (tabulate(data,headers=headers ,tablefmt='pretty'))

def weather_trend_info(location):
	query = 'SELECT HighLow24Hour,date_time, point_temperature,point_humidity,point_wind_speed FROM weather \
	WHERE location = \'{}\' '.format(location)

	connection = sqlite3.connect(DB_NAME)
	cursor = connection.cursor()
	result = cursor.execute(query).fetchall()
	connection.close()

	result_list = list(set(result))

	plot_dict = {}
	for record in result_list:
		value = list(record[2:])
		value.append(int(record[0][:2]))
		value.append(int(record[0][7:9]))

		date_time_str = record[1]
		date_time_obj = datetime.datetime.strptime(date_time_str, '%m/%d/%Y%H:%M:%p')
		plot_dict[date_time_obj] = value

	x_val=[]
	y_val_temp=[]
	y_val_high=[]
	y_val_low=[]
	for i in sorted (plot_dict.keys()):
		x_val.append(i)
		y_val_temp.append(plot_dict[i][0])
		y_val_high.append(plot_dict[i][3]) 
		y_val_low.append(plot_dict[i][4]) 

	scatter_data = go.Scatter(x=x_val, y=y_val_temp,mode='lines', name='Current')
	fig = go.Figure(data=scatter_data)
	fig.add_trace(go.Scatter(x=x_val, y=y_val_high,
	                    mode='lines',
	                    name='highest'))
	fig.add_trace(go.Scatter(x=x_val, y=y_val_low,
	                    mode='lines',
	                    name='lowest'))
	fig.show()

def temp_summary():
	query = 'SELECT AirTemperature \
	FROM weather'

	connection = sqlite3.connect(DB_NAME)
	cursor = connection.cursor()
	result = cursor.execute(query).fetchall()
	connection.close()
	temp_list = []
	for i in result:
		if i[0] != None:
			temp_list.append(i[0])

	y = np.array(temp_list)
	plt.hist(y)
	plt.title('Temperature Distribution in WA')
	plt.show()

def other_summary(which):
	query = 'SELECT Humidity,Visibility,WindSpeed \
	FROM weather'

	connection = sqlite3.connect(DB_NAME)
	cursor = connection.cursor()
	result = cursor.execute(query).fetchall()
	connection.close()


	if which == 'Humidity':
		humidity_list = []
		for i in result:
			if i[0] != None:
				a = float(i[0].strip('%'))/100
				humidity_list.append(a)

		fig = px.box(humidity_list ,points="suspectedoutliers")
		fig.update_layout(title_text="Humidity Summary")
		fig.show()

	elif which == 'Visibility':
		visibility_list = []
		for i in result:
			if i[1] != None:
				visibility_list.append(i[1])

		y_val = []
		y_val.append(visibility_list.count(0))
		y_val.append(visibility_list.count(1))
		y_val.append(visibility_list.count(2))
		y_val.append(visibility_list.count(3))
		y_val.append(visibility_list.count(4))

		bar_data = go.Bar(x=[1,2,3,4], y=y_val)
		fig = go.Figure(data=bar_data)

		fig.show()



	elif which == 'Windspeed':
		windspeed_list = []
		for i in result:
			if i[2] != None:
				windspeed_list.append(i[2])

		fig = px.box(windspeed_list ,points="suspectedoutliers")
		fig.update_layout(title_text="Windspeed Summary")
		fig.show()





response = ''
commandcheck = 0
while response != 'exit':
	response = input('Plese type your command: ')
	response = response.split()

	if 'location' in response:
		location = input('Type the location: ')
		if 'current' in response:
			weather_table_info(location)
		if 'past' in response:
			weather_trend_info(location)

	if 'temperature'  in response:
		temp_summary()

	if 'visibility' in response:
		other_summary('Visibility')
	if 'humidity' in response:
		other_summary('Humidity')
	if 'windspeed' in response:
		other_summary('Windspeed')


	if response == 'exit':
		print('bye')
	else:
		print('Try another one or exit')


	print('-'*50)

	











