'''
'''
import folium
from folium.plugins import MarkerCluster

from geopy.geocoders import Nominatim

def input() -> tuple:
	'''
	'''
	try:
		year = int(input("enter the year you are looking for"))
		coordinates = tuple(
		    input('Please enter your location (format: lat, long): ').split(','))
		return year, coordinates
	except:
		print("Please enter valid values")


def make_map(year: int, coordinates: tuple, top_places: list):
	'''
	'''
	my_map = folium.Map(location=coordinates)
	user_location = folium.FeatureGroup(name="User_Loc")

	user_location.add_child(
		folium.CircleMarker(
			location=coordinates,
            popup="Your home place",
            icon=folium.Icon(),
            fill_color="red",
            color="yellow",
            fill_opacity=1,
			))

	my_map.add_child(user_location)
	my_map.save('mymap.html')


def read_file(file_path="locations.list") -> list:
    '''
    '''
    result = []
    file = open(file_path, "r")
    while True:
        line = file.readline()
        if not line:
            break
        result.append(line)
    return result

def get_movies_by_year(year: int):
	'''
	'''
	movies_list = read_file()
	result = []
	for i in range(len(movies_list)):
		try:
			movie = movies_list[i].strip('\n').split('\t')
			movie_year = movie[0].split('(')[1].split(')')[0]
			if int(movie_year) == year:
				result.append(movie)
		except:
			continue
	return result

def get_movies_by_country(user_pos):
    '''
    '''
    movies = get_movies_by_year(2000)
    locator = Nominatim(user_agent="mapp")
    pos = str(user_pos[0]) + ", " + str(user_pos[1])
    location = locator.reverse(pos, language="en")
    location = str(location).split(",")
    if 'United States' in location[-1]:
    	location[-1] = 'USA'

    selected_movies = []
    for i in range(len(movies)):
        movie_country = movies[i][-1].split(' ')[-1]
        if movie_country == location[-1].strip(' '):
            selected_movies.append(movies[i])
    return selected_movies

def get_movie_location(user_pos):
    '''
    '''
    movies = get_movies_by_country(user_pos)
    movies_locations = []
    for i in range(len(movies)):
        location = None
        title = movies[i][0]
        movie_location = (movies[i][-1].split(", "))
        locator = Nominatim(user_agent="mapp")
        start = 0
        while location == None:
            location = locator.geocode(movie_location[start:])
            start += 1
            if start == len(movie_location):
                break
        if location != None:
        	movies_locations.append((title, (location.latitude, location.longitude)))
    return movies_locations



if __name__ == "__main__":
	print(get_movie_location((45,44)))
