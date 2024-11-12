import simplekml

# Sample Data: List of dictionaries containing lat, lng, alt, and distance
data = [
    {"lat": 12.9715987, "lng": 77.594566, "alt": 900, "distance": 1000},
    {"lat": 12.2958104, "lng": 76.6393805, "alt": 1200, "distance": 850},
    # Add more data points here...
]

# Create KML Object
kml = simplekml.Kml()

for point in data:
    # Create a new point for each data entry
    pnt = kml.newpoint()
    pnt.coords = [(point["lng"], point["lat"], point["alt"])]  # KML uses (longitude, latitude, altitude)
    pnt.altitudemode = simplekml.AltitudeMode.relativetoground
    
    # Name of the point can be the estimated distance
    pnt.name = f"Distance: {point['distance']} meters"
    pnt.description = f"Lat: {point['lat']}, Lng: {point['lng']}, Alt: {point['alt']}m"

# Save the KML file
kml.save("output.kml")

print("KML file generated: output.kml")