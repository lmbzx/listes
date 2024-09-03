import json
import os
from datetime import datetime

class JsonDataManager:
    def __init__(self, json_data_path):
        self.json_data_path = json_data_path

    def load_json(self):
        """Charge les données JSON à partir du fichier."""
        if not os.path.exists(self.json_data_path):
            raise FileNotFoundError(f"Le fichier JSON '{self.json_data_path}' n'existe pas.")
        
        with open(self.json_data_path, 'r') as f:
            data = json.load(f)
        
        return data

    def save_json(self, data):
        """Sauvegarde les données JSON dans un fichier, renomme l'ancien fichier avec un timestamp."""
        if os.path.exists(self.json_data_path):
            # Renommer l'ancien fichier avec un timestamp
            timestamp = datetime.now().strftime('%y%m%d%H%M%S')
            new_name = f"prev{timestamp}.json"
            os.rename(self.json_data_path, new_name)
            print(f"Fichier JSON précédent renommé en '{new_name}'.")

        with open(self.json_data_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Les données JSON ont été sauvegardées dans '{self.json_data_path}'.")

