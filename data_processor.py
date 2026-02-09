import gpxpy
import pandas as pd

def parse_gpx(file):
    gpx = gpxpy.parse(file)
    data = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data.append({
                    "timestamp": point.time,
                    "latitude": point.latitude,
                    "longitude": point.longitude,
                    "elevation": point.elevation
                })
    return pd.DataFrame(data)