from service_account_manager import ServiceAccountManager
from config_manager import ConfigManager
from json_data_manager import JsonDataManager
from google_sheet_updater import GoogleSheetUpdater
import os

class SheetManager:
    def __init__(self, encrypted_key_path, config_path, json_data_path):
        # Récupération du mot de passe de décryptage à partir de la variable d'environnement
        aes_password = os.environ.get('AES_PASSWORD')
        if not aes_password:
            raise ValueError("Le mot de passe AES n'est pas défini dans les variables d'environnement.")

        # Chargement de la clé de service Google à partir du fichier chiffré
        self.service_account_manager = ServiceAccountManager(encrypted_key_path, aes_password)
        #.encode('utf-8'))
        service_account_info = self.service_account_manager.decrypt_service_account_key()

        # Chargement de la configuration
        self.config_manager = ConfigManager(config_path)
        self.configs = self.config_manager.get_config()

        # Chargement des données JSON
        self.json_data_manager = JsonDataManager(json_data_path)
        json_data = self.json_data_manager.load_json()

        # Initialisation du Google Sheet Updater
        self.sheet_updater = GoogleSheetUpdater(service_account_info)
        self.json_data = json_data

    def run(self):
        """Exécute la mise à jour de la feuille Google."""
        for config in self.configs:
           self.sheet_updater.update_google_sheet(self.json_data,config)


