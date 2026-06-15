import os
import sys
import argparse

# Force l'ajout de la racine au chemin de recherche des modules Python
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

def main():
    parser = argparse.ArgumentParser(
        description="IntelliTrade - Outils de pilotage du pipeline CAC 40 & IA"
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--dashboard', 
        action='store_true', 
        help="Lancer l'application web Dash (Par défaut)"
    )
    group.add_argument(
        '--ingest-history', 
        action='store_true', 
        help="Télécharger 2 ans d'historique boursier et les stocker dans BigQuery"
    )
    group.add_argument(
        '--ingest-realtime', 
        action='store_true', 
        help="Scraper Boursorama en temps réel, stocker dans BigQuery et envoyer le rapport email"
    )
    
    args = parser.parse_args()
    
    # Action par défaut : lancer le Dashboard
    if not (args.ingest_history or args.ingest_realtime) or args.dashboard:
        print("=== IntelliTrade : Lancement du Dashboard Premium ===")
        from src.dashboard.app import app
        # Récupère le serveur Flask sous-jacent pour la compatibilité WSGI (gunicorn)
        server = app.server
        app.run_server(host='0.0.0.0', port=8050, debug=True)
        
    elif args.ingest_history:
        print("=== IntelliTrade : Début de l'ingestion historique yfinance ===")
        from src.ingestion.extract_history import extract_and_load_history
        success = extract_and_load_history()
        if success:
            print("=== Ingestion historique terminée avec succès ===")
            sys.exit(0)
        else:
            print("=== Échec de l'ingestion historique ===")
            sys.exit(1)
            
    elif args.ingest_realtime:
        print("=== IntelliTrade : Lancement du job scraping temps réel ===")
        from src.ingestion.extract_realtime import job
        excel_file = job()
        if excel_file:
            print(f"=== Scraping complété. Fichier généré : {excel_file} ===")
            # Envoi du rapport si l'envoi est configuré (optionnel dans le job original)
            from src.utils.email_sender import send_market_report
            try:
                send_market_report(excel_file)
                print("=== Rapport email envoyé avec succès ===")
            except Exception as e:
                print(f"=== Envoi d'email ignoré ou échoué : {e} ===")
            sys.exit(0)
        else:
            print("=== Échec du job temps réel ===")
            sys.exit(1)

if __name__ == '__main__':
    main()
