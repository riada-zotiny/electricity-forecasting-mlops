import requests
import pandas as pd
import time

# API endpoint - v2.0 (v2.1 ne marche pas)
API_URL = "https://odre.opendatasoft.com/api/explore/v2.0/catalog/datasets/eco2mix-national-tr/records"

# Headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def fetch_eco2mix_data(limit=100, offset=0):
    """
    Récupère les données eco2mix de l'API OpenDataSoft
    
    Args:
        limit: Nombre de records à récupérer par requête (max 100)
        offset: Point de départ pour la pagination
    
    Returns:
        DataFrame avec les données eco2mix
    """
    # Limiter à 100 max (limite de l'API)
    limit = min(limit, 100)
    
    params = {
        "limit": limit,
        "offset": offset,
        "order_by": "date_heure desc"
    }
    
    try:
        print(f"Requête: offset={offset}, limit={limit}")
        response = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extraire les records
        records = data.get('results', [])
        
        if not records:
            print("Aucune donnée trouvée")
            return pd.DataFrame()
        
        # Convertir en DataFrame
        df = pd.DataFrame(records)
        
        print(f"✓ {len(df)} records reçus")
        
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")
        return pd.DataFrame()

def fetch_all_eco2mix_data(batch_size=100, max_batches=None):
    """
    Récupère TOUTES les données avec pagination
    
    Args:
        batch_size: Nombre de records par batch (max 100)
        max_batches: Nombre max de batches à récupérer (None = tous)
    
    Returns:
        DataFrame avec toutes les données
    """
    all_data = []
    offset = 0
    batch_count = 0
    
    while True:
        if max_batches and batch_count >= max_batches:
            print(f"\n⚠ Limite de {max_batches} batches atteinte")
            break
            
        print(f"\n--- Batch {batch_count + 1} ---")
        df_batch = fetch_eco2mix_data(limit=batch_size, offset=offset)
        
        if df_batch.empty:
            print("✓ Fin de la pagination atteinte")
            break
        
        all_data.append(df_batch)
        batch_count += 1
        
        if len(df_batch) < batch_size:
            print(f"✓ Dernier batch avec {len(df_batch)} records")
            break
        
        offset += batch_size
        time.sleep(0.3)  # Délai entre requêtes
    
    if all_data:
        df_final = pd.concat(all_data, ignore_index=True)
        print(f"\n✓ TOTAL: {len(df_final)} records en {batch_count} batch(es)")
        return df_final
    
    return pd.DataFrame()

def save_to_csv(df, filename='eco2mix_data.csv'):
    """Sauvegarde les données en CSV"""
    if not df.empty:
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Données sauvegardées dans {filename}")
    else:
        print("Pas de données à sauvegarder")

if __name__ == "__main__":
    # Récupérer les données (avec pagination pour tout récupérer)
    df = fetch_all_eco2mix_data()
    
    # Sauvegarder
    if not df.empty:
        save_to_csv(df)
        
        # Afficher les infos
        print(f"\nInfos sur les données:")
        print(df.info())
        print(f"\nAperçu des données:\n{df.head()}")