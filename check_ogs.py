import requests
import os
import json
import time

# --- Configuration du script de surveillance ---
# Ajoutez les IDs des joueurs que vous voulez espionner dans cette liste.
# Vous pouvez aussi ajouter un nom pour faciliter l'identification dans la notification.
JOUEURS_A_SURVEILLER = {
    "1484188": "Randommover",
    "1854131": "Inseong",
    "1088109": "Moad",
    "1812060": "Keil",
    "991056": "Keil1",
    "1734477": "Pierre-Loic",
    "56011": "Olivier",
    "1123891": "Lilanlu"
}

FICHIER_COMPTEUR = "game_counts.json"

# --- Configuration de la notification push (NTFY) ---
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"


def envoyer_notification_push(titre, message):
    if not NTFY_TOPIC:
        print("Erreur : Le sujet NTFY n'est pas configuré. Veuillez vérifier le secret GitHub.")
        return
    try:
        requests.post(
            NTFY_URL,
            data=message.encode('utf-8'),
            headers={"Title": titre, "Priority": "high"}
        )
        print("Notification push envoyée avec succès !")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'envoi de la notification push : {e}")


# --- Fonction principale ---
def run_check():
    # 1. Lire les données de l'exécution précédente
    try:
        if os.path.exists(FICHIER_COMPTEUR):
            with open(FICHIER_COMPTEUR, 'r') as f:
                etats_precedents = json.load(f)
        else:
            etats_precedents = {}
    except (json.JSONDecodeError, FileNotFoundError):
        etats_precedents = {}

    etats_actuels = {}

    # 2. Vérifier chaque joueur de la liste
    for joueur_id, nom_joueur in JOUEURS_A_SURVEILLER.items():
        url_api = f"https://online-go.com/api/v1/players/{joueur_id}/games"
        nombre_precedent = etats_precedents.get(joueur_id, 0)

        try:
            reponse = requests.get(url_api, timeout=10)
            reponse.raise_for_status()
            donnees = reponse.json()
            nombre_actuel = donnees.get('count')
            etats_actuels[joueur_id] = nombre_actuel

            print(f"Vérification de {nom_joueur} ({joueur_id}). Parties : {nombre_actuel}.")

            # 3. Comparer et envoyer une notification si nécessaire
            if nombre_actuel > nombre_precedent:
                titre = f"Nouvelle partie pour {nom_joueur} !"
                message = f"{nom_joueur} a commencé une nouvelle partie. Total : {nombre_actuel}."
                print(f"\n--- ATTENTION ! {message} ---")
                envoyer_notification_push(titre, message)
            elif nombre_actuel < nombre_precedent:
                print(f"Une partie de {nom_joueur} a été terminée. Total : {nombre_actuel}.")

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion pour {nom_joueur} ({joueur_id}) : {e}.")

    # 4. Enregistrer le nouvel état pour la prochaine exécution
    with open(FICHIER_COMPTEUR, 'w') as f:
        json.dump(etats_actuels, f, indent=4)
    print("État de tous les joueurs mis à jour.")


if __name__ == "__main__":
    run_check()

