from os import path
import math
from math import sin, cos, sqrt, atan2, radians
from datetime import datetime as dt
import requests as rq
import time
import pandas as pd
import folium
import streamlit as st
import streamlit_folium as sf
import geopy.distance

urlGeoJSON = "https://download.data.grandlyon.com/wfs/rdata?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=jcd_jcdecaux.jcdvelov&outputFormat=application/json;%20subtype=geojson&SRSNAME=EPSG:4171&startIndex=0"

green = "https://raw.githubusercontent.com/raneio/free-sketch-map-marker/433d0a1b6e8738b2b610ee2215a2d936d31d8607/svg/map-marker-green.svg"
blue = "https://raw.githubusercontent.com/raneio/free-sketch-map-marker/433d0a1b6e8738b2b610ee2215a2d936d31d8607/svg/map-marker-blue.svg"
orange = "https://raw.githubusercontent.com/raneio/free-sketch-map-marker/433d0a1b6e8738b2b610ee2215a2d936d31d8607/svg/map-marker-orange.svg"
red = "https://raw.githubusercontent.com/raneio/free-sketch-map-marker/433d0a1b6e8738b2b610ee2215a2d936d31d8607/svg/map-marker-red.svg"

colorDict = {
    'green': green,
    'blue': blue,
    'orange': orange,
    'red': red
    }

def record(): # Only one request on the API and returns a DataFrame
    reponse = rq.get(urlGeoJSON)

    if reponse.status_code == 200:
        dataGeoJSON = reponse.json()
        data = pd.json_normalize(dataGeoJSON['features'])
        return data
    
def prepa(dataframe): # Data preparation
    
    # Rename
    for column in dataframe.columns[1:]:
        dataframe.rename(columns = {column: column.split('.')[1]}, inplace = True)
    dataframe.rename(columns = {
        'available_bikes': 'bikes',
        'available_bike_stands': 'stands'}, inplace = True)
    
    # Empty values
    dataframe.loc[dataframe['bikes'] == '','bikes'] = 0
    dataframe.loc[dataframe['stands'] == '','stands'] = 0
        
    # Retype
    dataframe['lat'] = dataframe['lat'].astype(float)
    dataframe['lng'] = dataframe['lng'].astype(float)
    dataframe.drop(columns = ['coordinates'], inplace = True)
    dataframe['bikes'] = dataframe['bikes'].astype(int)
    dataframe['stands'] = dataframe['stands'].astype(int)

    dataframe['color_bikes'] = [
        'red' if bikes == 0 else
        'orange' if bikes <= 5 else
        'blue' if bikes <= 10 else
        'green' for bikes in dataframe['bikes']]

    dataframe['color_stands'] = [
        'red' if bikes == 0 else
        'orange' if bikes <= 5 else
        'blue' if bikes <= 10 else
        'green' for bikes in dataframe['stands']]

    return dataframe

def getCoords(address): #Return coords of an address
	link = 'https://api-adresse.data.gouv.fr/search/'
	params = {
		'q': address
	}
	r = rq.get(link,params = params).json()
	return r['features'][0]['geometry']['coordinates'][::-1]

def addDistance(dataframe,point): # Add a Series distance based on distance from point

	distance = []
	for index, row in dataframe.iterrows():

		new_distance = geopy.distance.distance([row['lat'],row['lng']],point).km
		distance.append(new_distance)

	dataframe['distance'] = distance
	return dataframe.sort_values(by = 'distance', ascending = True)

def showMap(column_selected,df): # Displays a map based on bikes or stands availables from a DataFrame
    
    mapLyon = folium.Map([df.lat.mean(),df.lng.mean()],zoom_start = 13)

    # TITLE
    title = "<h3>Stations Velo'v</h3>"
    mapLyon.get_root().html.add_child(folium.Element(title))

    # MARKERS
    for index, row in df.iterrows():
        line1 = f"<b>Station :</b> {row['name']}"
        line2 = f"<b>Nombre de Velo'v disponibles :</b> {row['bikes']}"
        line3 = f"<b>Nombre de stands disponibles :</b> {row['stands']}"      
    
        folium.Marker(
            location = [row['lat'], row['lng']],
            popup = folium.Popup(
                line1 + '<br>' + line2 + '<br>' + line3,
                max_width = max(len(line1),len(line2),len(line3))*20
            ),
            icon = folium.CustomIcon(colorDict[row[column_selected]])
        ).add_to(mapLyon)
    
    return sf.folium_static(mapLyon)

def main():

	# TITLES AND BUTTONS
	st.title("Disponibilité des bornes Velo'v")

	def_address = "Je saisie une adresse... (optionnel)"
	address = st.text_input("", def_address)

	st.write("Je cherche...")
	button_left, button_right = st.beta_columns(2)

	with button_left:
		left = st.button("Un vélo disponible")
	with button_right:
		right = st.button("Un emplacement libre")

	# ACQUISITION AND DISPLAYING MAP
	data = record()
	data = prepa(data)

	if (address != def_address) and (address != ""):
		coords = getCoords(address)
		data = addDistance(data,coords).head(5)
	if left:
		myMap = showMap("color_bikes",data)
	elif right:
		myMap = showMap("color_stands",data)

main()
