import os
from google.cloud import bigquery
from google.oauth2 import service_account

def get_gcp_config():
    # Détermine le chemin vers config/gcp_service_account.json
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    keyfile_path = os.path.abspath(os.path.join(base_dir, 'config', 'gcp_service_account.json'))
    
    project_id = os.environ.get('GCP_PROJECT_ID')
    return keyfile_path, project_id

def get_bq_client():
    keyfile_path, project_id = get_gcp_config()
    
    # Authentification par fichier de clé de service si présent (développement local)
    if os.path.exists(keyfile_path):
        print(f"Connexion BigQuery via compte de service : {keyfile_path}")
        credentials = service_account.Credentials.from_service_account_file(keyfile_path)
        client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        return client
        
    # Repli sur les identifiants par défaut GCP (Cloud Run, Cloud Functions, Cloud Shell)
    print("Connexion BigQuery via Application Default Credentials (ADC)")
    if project_id:
        return bigquery.Client(project=project_id)
    return bigquery.Client()

def get_project_id():
    keyfile_path, project_id = get_gcp_config()
    if os.path.exists(keyfile_path):
        credentials = service_account.Credentials.from_service_account_file(keyfile_path)
        return credentials.project_id
    return project_id or "votre-projet-gcp"
