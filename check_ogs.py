import requests
import os
import smtplib
import ssl
from email.message import EmailMessage

# --- Configuration du script de surveillance ---
ID_DU_JOUEUR = "1484188"
url_api = f"https://online-go.com/api/v1/players/{ID_DU_JOUEUR}/games"
FICHIER_COMPTEUR = "game_count.txt"

# --- Configuration de la notification push (NTFY) ---
# Le sujet est récupéré des secrets GitHub Actions
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

def envoyer_notification_push(titre, message):
    if not NTFY_TOPIC:
        print("Erreur : Le sujet NTFY n'est pas configuré. Veuillez vérifier le secret GitHub.")
        return

    try:
        reponse = requests.post(
            NTFY_URL,
            data=message.encode('utf-8'),
            headers={
                "Title": titre,
                "Priority": "high",
            }
        )
        reponse.raise_for_status()
        print("Notification push envoyée avec succès !")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'envoi de la notification push : {e}")

# --- Fonction principale ---
def run_check():
    # 1. Lire le nombre de parties de l'exécution précédente
    nombre_de_parties_initial = 0
    if os.path.exists(FICHIER_COMPTEUR):
        with open(FICHIER_COMPTEUR, 'r') as f:
            nombre_de_parties_initial = int(f.read().strip())

    print(f"Nombre de parties de l'exécution précédente : {nombre_de_parties_initial}")

    # 2. Vérifier le nombre de parties actuel via l'API
    try:
        reponse = requests.get(url_api, timeout=10)
        reponse.raise_for_status()
        donnees = reponse.json()
        nombre_de_parties_actuel = donnees.get('count')
        print(f"Nombre de parties actuel : {nombre_de_parties_actuel}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion à l'API : {e}")
        exit()

    # 3. Comparer et envoyer une notification si nécessaire
    if nombre_de_parties_actuel > nombre_de_parties_initial:
        titre = "Nouvelle partie OGS détectée !"
        message = f"Le joueur a commencé une nouvelle partie. Total actuel : {nombre_de_parties_actuel}."
        print(f"\n--- ATTENTION ! {message} ---")
        envoyer_notification_push(titre, message)
    elif nombre_de_parties_actuel < nombre_de_parties_initial:
        print(f"Une partie a été terminée. Le joueur a maintenant {nombre_de_parties_actuel} parties.")
    else:
        print("Pas de changement dans le nombre de parties.")

    # 4. Enregistrer le nombre actuel pour la prochaine exécution
    with open(FICHIER_COMPTEUR, 'w') as f:
        f.write(str(nombre_de_parties_actuel))
    print(f"Compteur de parties mis à jour dans le fichier {FICHIER_COMPTEUR}.")

if __name__ == "__main__":
    run_check()