import requests
import time
import threading

# Configuration
BASE_URL = "http://10.10.195.32"
USERNAME = "ubnt"
PASSWORD = "ubnt"

class ConnectedSocket:
    """
    Classe pour gérer les interactions avec une prise connectée via une API HTTP.

    Attributs :
        session (requests.Session) : La session HTTP utilisée pour les requêtes.
        session_id (str) : L'ID de session obtenu après authentification.
    """

    def __init__(self):
        self.session = requests.Session()
        self.session_id = None

    def authenticate(self):
        """
        Authentifie l'utilisateur et établit une session en utilisant les informations de connexion.
        Enregistre l'ID de session pour les requêtes ultérieures.
        """
        login_url = f"{BASE_URL}/login.cgi"
        data = {
            "username": USERNAME,
            "password": PASSWORD
        }
        response = self.session.post(login_url, data=data)
        response.raise_for_status()

        # Affiche les cookies pour débogage
        print(f"Cookies reçus : {self.session.cookies}")
        for cookie in self.session.cookies:
            if cookie.name == 'AIROS_SESSIONID':
                self.session_id = cookie.value
        if self.session_id:
            print("Authentification réussie")
        else:
            print("Échec de l'obtention de l'ID de session")

    def get_socket_info_key(self, socket_id, key):
        """
        Obtient une information spécifique d'une prise connectée.

        Args:
            socket_id (str): L'ID de la prise connectée.
            key (str): La clé de l'information à récupérer.

        Returns:
            dict or None: La valeur de l'information demandée ou None si une erreur survient.
        """
        if not self.session_id:
            print("Vous devez vous authentifier d'abord")
            return None
        url = f"{BASE_URL}/sensors/{socket_id}/{key}"
        response = self.session.get(url)
        response.raise_for_status()

        # Vérification de si la réponse est une page de connexion
        if "Login" in response.text:
            print("Page de connexion reçue, réauthentification requise")
            self.authenticate()
            response = self.session.get(url)
            response.raise_for_status()

        # Vérification de si la réponse est vide ou non JSON
        if response.text.strip() == "":
            print("Réponse vide reçue")
            return None
        
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            print("Échec de l'analyse de la réponse en JSON")
            print("Texte de la réponse :", response.text)
            return None

    def toggle_socket_state(self, socket_id, state=None):
        """
        Bascule l'état d'une prise connectée.

        Args:
            socket_id (str): L'ID de la prise connectée.
            state (int, optional): L'état à définir (0 ou 1). Si None, bascule l'état actuel.
        """
        if not self.session_id:
            print("Vous devez vous authentifier d'abord")
            return
        current_state = self.get_socket_info_key(socket_id, "output")
        if current_state is None:
            print("Échec de la récupération de l'état actuel")
            return

        print(f"État actuel de la prise {socket_id} : {current_state}")

        # Extraction de l'état actuel de la réponse JSON
        if isinstance(current_state, dict) and 'sensors' in current_state:
            sensors = current_state.get('sensors', [])
            if len(sensors) > 0 and 'output' in sensors[0]:
                current_state = sensors[0]['output']
            else:
                print("État actuel non trouvé dans la réponse")
                return
        else:
            print("État actuel non trouvé dans la réponse")
            return

        # Nouvel état
        if state is None:
            new_state = 1 if current_state == 0 else 0
        else:
            new_state = state
            
        data = {"output": new_state}
        url = f"{BASE_URL}/sensors/{socket_id}"
        response = self.session.put(url, data=data)
        response.raise_for_status()
        print(f"État de la prise {socket_id} défini à {new_state}")

    def blink_socket(self, socket_id):
        """
        Fait clignoter une prise connectée.

        Args:
            socket_id (str): L'ID de la prise connectée.
        """
        self.blinking = True
        self.blink_thread = threading.Thread(target=self._blink_socket, args=(socket_id,), daemon=True)
        self.blink_thread.start()

    def _blink_socket(self, socket_id):
        """
        Fonction interne pour faire clignoter une prise connectée en basculant son état toutes les secondes.

        Args:
            socket_id (str): L'ID de la prise connectée.
        """
        while self.blinking:
            self.toggle_socket_state(socket_id)
            time.sleep(1)

    def stop_blinking(self):
        """
        Arrête le clignotement de la prise connectée.
        """
        self.blinking = False
        if self.blink_thread:
            self.blink_thread.join()
            self.blink_thread = None