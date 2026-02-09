from supabase import create_client, Client
import datetime

# Remplace par tes vrais identifiants Supabase
url = "https://editeaqmqnnlvllefjop.supabase.co"
key = "sb_publishable_e4BH8AM2iuDdS3gav7QM_w_6NXg6w4a"
supabase = create_client(url, key)

# Donnée de test (ex: ce que j'ai fait aujourd'hui)
data_to_send = {
    "date": str(datetime.date.today()),
    "steps": 8500,
    "screen_time": 120.5,
    "distance_gps": 4.2
}

# Envoi vers la table 'daily_metrics'
try:
    response = supabase.table("daily_metrics").insert(data_to_send).execute()
    print("✅ Succès ! Donnée envoyée au cloud.")
except Exception as e:
    print(f"❌ Erreur : {e}")