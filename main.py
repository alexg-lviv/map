'''
module for searching few closest spots of filmmaking to your location
'''
import folium
import haversine
from folium.plugins import MarkerCluster

from geopy.geocoders import Nominatim


def my_input() -> tuple:
    '''
    an input function to get the year and location to search for
    returns year and coordinates
    '''
    try:
        year = int(input("enter the year you are looking for "))
        coordinates = input('Please enter your location (format: lat, long): ').split(',')
        coordinates[0] = float(coordinates[0])
        coordinates[1] = float(coordinates[1])

        return year, coordinates
    except:
        print("Please enter valid values")


def make_map(year: int, user_pos: tuple, top_places: list):
    '''
    a function to make an html map
    returns the name of created file
    '''
    my_map = folium.Map(location=user_pos)
    user_location = folium.FeatureGroup(name="User_Loc")
    population = folium.FeatureGroup(name="Population")
    markers = folium.plugins.MarkerCluster().add_to(user_location)

    user_location.add_child(
        folium.CircleMarker(
            location=user_pos,
            popup="Your home place",
            icon=folium.Icon(),
            fill_color="red",
            color="yellow",
            fill_opacity=1,
            ))
    for i in range(len(top_places)):
        popup = top_places[i][0]
        folium.Marker(location=top_places[i][2], popup=popup).add_to(markers)

    population.add_child(
        folium.GeoJson(
            data=open("world.json", "r", encoding="utf-8-sig").read(),
            style_function=lambda x: {
                "fillColor": "green"
                if x["properties"]["POP2005"] < 10000000
                else "orange"
                if 10000000 <= x["properties"]["POP2005"] < 20000000
                else "red"
            },
        )
    )
    
    my_map.add_child(user_location)
    my_map.add_child(population)
    my_map.add_child(folium.LayerControl())
    my_map.save(f"{year}_movies_map.html")

    return f"{year}_movies_map.html"


def read_file(file_path="locations.list") -> list:
    '''
    reads the films database, returns a list with each line as element
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
    filters movies by year
    returns list only with films of specified year
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

def get_movies_by_country(user_pos, year):
    '''
    filters movies by country
    returns the list only with films of that year from that country
    '''
    movies = get_movies_by_year(year)
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

def get_movie_location(user_pos, year):
    '''
    gets a location of movies
    returns a list of titles, and coordinates of movie
    '''
    movies = get_movies_by_country(user_pos, year)
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


def calculate_distances(user_pos, year):
    '''
    calculates distances betwen places where movies were filmed and user position
    returns a list with information about film, distance, and location
    '''
    locations = get_movie_location(user_pos, year)
    distances = []
    for i in range(len(locations)):
        distance = round(haversine.haversine(user_pos, locations[i][1]))
        distances.append((locations[i][0], distance, locations[i][1]))
    distances.sort(key=sort_function)
    return distances[:10]

def sort_function(value):
    '''
    a sort function, key is distance
    '''
    return value[1]


def main():
    '''
    main function for this module
	it uses all of the functions above and makes them all work
    '''
    year, user_pos = my_input()
    top_places = calculate_distances(user_pos, year)
    print(make_map(year, user_pos, top_places))

if __name__ == "__main__":
    main()
