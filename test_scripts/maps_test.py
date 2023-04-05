import googlemaps
import pprint
import json
import geopy.distance

with open("../apps/static/assets/tokens/tokens") as tokens_file:
    tokens = json.load(tokens_file)

gmaps = googlemaps.Client(key=tokens["gmaps"])

nearby_result = gmaps.places_nearby(
    location=(35.9320068046707, -79.03559110882956),
    radius=500,
    keyword="park")

pp = pprint.PrettyPrinter(indent=1)
# pp.pprint(nearby_result["results"])
for place_result in nearby_result["results"]:
    user_loc = (35.9320068046707, -79.03559110882956)
    place_loc = (place_result["geometry"]["location"]["lat"], place_result["geometry"]["location"]["lng"])
    print(geopy.distance.distance(user_loc, place_loc).miles, place_result["name"])
