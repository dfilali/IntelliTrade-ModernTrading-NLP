import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

def send_market_report(excel_path):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_path = os.path.abspath(os.path.join(base_dir, 'config', 'mail_config.json'))
    
    if not os.path.exists(config_path):
        print(f"Configuration email introuvable à {config_path}")
        return False
        
    with open(config_path) as json_file:
        gmail_cfg = json.load(json_file)
        
    smtp_port = gmail_cfg.get("port", 587)
    smtp_server = gmail_cfg.get("server", "smtp.gmail.com")
    email_from = gmail_cfg.get("sender")
    email_list = gmail_cfg.get("reciever", [])
    pswd = gmail_cfg.get("password")
    
    if not email_from or not email_list or not pswd:
        print("Paramètres email incomplets dans la configuration")
        return False

    date_str = datetime.now().strftime("%d/%m/%Y")
    body = f"""Bonjour,\n
        Le marché EuroNextParis vient de cloturé.\n
        Veuillez trouver ci-joint le fichier contenant les données des entreprises du CAC40 pour le {date_str}.\n
        Cordialement,\n
        Trading-Bot\n
        IntelliTrade"""

    success = True
    try:
        print("Connexion au serveur SMTP...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_from, pswd)
        print("Connexion réussie au serveur SMTP")
        
        for person in email_list:
            msg = MIMEMultipart()
            msg['From'] = email_from
            msg['To'] = person
            msg['Subject'] = f"INFO : Valeurs des actions du CAC40 du {date_str} Groupe 02"
            
            msg.attach(MIMEText(body, 'plain'))
            
            if os.path.exists(excel_path):
                with open(excel_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    filename = os.path.basename(excel_path)
                    part.add_header('Content-Disposition', f"attachment; filename={filename}")
                    msg.attach(part)
            else:
                print(f"Attention: Pièce jointe non trouvée : {excel_path}")
            
            print(f"Envoi du mail à : {person}...")
            server.sendmail(email_from, person, msg.as_string())
            print(f"Mail envoyé à : {person}")
            
        server.quit()
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")
        success = False
        
    return success
