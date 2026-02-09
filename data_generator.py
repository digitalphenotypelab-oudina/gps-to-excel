import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_fake_gps_data(num_points=100, start_lat=48.8566, start_lon=2.3522):
    """
    Génère une trace GPS aléatoire (marche aléatoire) à partir d'un point (Paris par défaut).
    """
    data = []
    current_time = datetime.now()
    
    # Point de départ
    lat = start_lat
    lon = start_lon
    
    for _ in range(num_points):
        # Simulation d'un déplacement léger (environ 5-10 mètres)
        # 0.0001 degré lat ~= 11 mètres
        delta_lat = np.random.uniform(-0.0001, 0.0001) 
        delta_lon = np.random.uniform(-0.0001, 0.0001)
        
        lat += delta_lat
        lon += delta_lon
        
        # On ajoute 1 minute entre chaque point
        current_time += timedelta(minutes=1)
        
        data.append({
            "timestamp": current_time,
            "latitude": lat,
            "longitude": lon,
            "accuracy": np.random.uniform(2, 10) # Précision du GPS en mètres
        })
        
    return pd.DataFrame(data)