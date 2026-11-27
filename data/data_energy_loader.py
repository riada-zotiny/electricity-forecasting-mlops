import requests
import pandas as pd
import time

# v2.1 : réponse sous la clé "results", limit <= 100 et offset + limit <= 10000
API_URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records"

# Headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def build_where(start=None, end=None, only_measured=False):
    """Construit le filtre ODSQL. start/end au format 'YYYY-MM-DD' (end inclus)."""
    clauses = []
    if start:
        clauses.append(f"date_heure >= '{start}'")
    if end:
        end_excl = (pd.Timestamp(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        clauses.append(f"date_heure < '{end_excl}'")
    if only_measured:
        clauses.append("consommation is not null")
    return " AND ".join(clauses) or None

def fetch_eco2mix_data(limit=100, offset=0, where=None):
    """
    Récupère les données eco2mix de l'API OpenDataSoft
    """
    limit = min(limit, 100)
    
    params = {
        "limit": limit,
        "offset": offset,
        "order_by": "date_heure desc"
    }
    if where:
        params["where"] = where
    
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
        
        print(f" {len(df)} records reçus")
        
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"Erreur: {e}")
        return pd.DataFrame()

def fetch_all_eco2mix_data(batch_size=100, max_batches=None, start=None, end=None, only_measured=False):
    """
    Récupère les données avec pagination, sur une période optionnelle
    (start/end au format 'YYYY-MM-DD', bornes incluses).
    """
    where = build_where(start, end, only_measured)
    all_data = []
    offset = 0
    batch_count = 0
    
    while True:
        if max_batches and batch_count >= max_batches:
            print(f"\n Limite de {max_batches} batches atteinte")
            break
            
        print(f"\n--- Batch {batch_count + 1} ---")
        df_batch = fetch_eco2mix_data(limit=batch_size, offset=offset, where=where)
        
        if df_batch.empty:
            print(" Fin de la pagination atteinte")
            break
        
        all_data.append(df_batch)
        batch_count += 1
        
        if len(df_batch) < batch_size:
            print(f" Dernier batch avec {len(df_batch)} records")
            break
        
        offset += batch_size
        time.sleep(0.3)  # Délai entre requêtes
    
    if all_data:
        df_final = pd.concat(all_data, ignore_index=True)
        print(f"\n TOTAL: {len(df_final)} records en {batch_count} batch(es)")
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
    df = fetch_all_eco2mix_data(start="2026-11-01", end="2026-11-15", only_measured=True)
    
    # Sauvegarder
    if not df.empty:
        save_to_csv(df)
        
        # Afficher les infos
        print(f"\nInfos sur les données:")
        print(df.info())
        print(f"\nAperçu des données:\n{df.head()}")