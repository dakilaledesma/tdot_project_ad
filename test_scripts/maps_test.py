import googlemaps
import pprint
import json

with open("../apps/static/assets/tokens/tokens") as tokens_file:
    tokens = json.load(tokens_file)

gmaps = googlemaps.Client(key=tokens["gmaps"])

nearby_result = gmaps.places_nearby(location=(40.714224, -73.961452),
                             radius=500,
                             keyword="park")

pp = pprint.PrettyPrinter(indent=1)
# pp.pprint(nearby_result["results"])
for place_result in nearby_result["results"]:
    print(place_result["name"])