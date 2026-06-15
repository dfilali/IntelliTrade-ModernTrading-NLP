import os
import sys
import yfinance as yf
import pandas as pd

import pandas_gbq

# Ajout du chemin du projet au PYTHONPATH si exécuté en tant que script direct
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from src.utils.db import get_project_id

def extract_and_load_history():
    company_referal_path = os.path.join(base_dir, 'data', 'input', 'liste_cac40.xlsx')
    
    if not os.path.exists(company_referal_path):
        print(f"Fichier de référence des entreprises introuvable : {company_referal_path}")
        return False
        
    print(f"Chargement de la liste depuis {company_referal_path}...")
    cac40_data = pd.read_excel(company_referal_path)
    
    # DataFrame pour stocker les données historiques
    historical_data = pd.DataFrame(columns=['Date et Heure', 'Open', 'High', 'Low', 'Close', 'Volume', 'Name'])
    
    end_date = pd.to_datetime('today')
    # Récupérer 2 ans d'historique
    start_date = end_date - pd.DateOffset(days=730) + pd.DateOffset(hours=9)
    
    print("Téléchargement des données yfinance pour les tickers CAC 40...")
    for index, row in cac40_data.iterrows():
        symbol = row['Symbol']
        name = row['Name']
        try:
            print(f"Téléchargement de {name} ({symbol})...")
            data = yf.download(symbol, start=start_date, end=end_date, interval='1h')
            if data.empty:
                print(f"Aucune donnée pour {symbol}")
                continue
                
            # Si les colonnes sont un MultiIndex, on aplatit pour ne garder que la métrique (Open, Close, etc.)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
                
            # Filtrer les données pour ne conserver que celles de 9h à 17h
            data = data.between_time('09:00', '17:00')
            
            # Ajouter la colonne "Name"
            data['Name'] = name
            
            # Concaténer
            historical_data = pd.concat([historical_data, data], ignore_index=False)
        except Exception as e:
            print(f"Erreur lors du téléchargement pour {symbol}: {e}")
            
    if historical_data.empty:
        print("Erreur: aucune donnée historique n'a pu être récupérée.")
        return False
        
    # Convertir l'index en DatetimeIndex et formater la date
    historical_data.index = pd.to_datetime(historical_data.index)
    historical_data['Date et Heure'] = historical_data.index.strftime('%Y-%m-%d %H:%M:%S')
    
    # Réorganiser les colonnes
    historical_data = historical_data[['Name', 'Open', 'High', 'Low', 'Close', 'Volume', 'Date et Heure']]
    
    # Insérer dans Google BigQuery
    project_id = get_project_id()
    nom_table = 'raw_trading.data_trading'
    
    try:
        print(f"Chargement des données dans BigQuery : '{nom_table}' (if_exists='replace')...")
        pandas_gbq.to_gbq(historical_data, nom_table, project_id=project_id, if_exists='replace')
        print(f"Données historiques injectées avec succès ({len(historical_data)} lignes).")
    except Exception as e:
        print(f"Erreur lors de l'insertion dans BigQuery : {e}")
        return False
        
    # Sauvegarde Excel locale de secours
    excel_output_path = os.path.join(base_dir, 'historical_data_cac40.xlsx')
    historical_data.to_excel(excel_output_path, index=False)
    print(f"Données historiques sauvegardées dans '{excel_output_path}'.")
    return True

if __name__ == '__main__':
    extract_and_load_history()
