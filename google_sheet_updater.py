import gspread
from google.oauth2.service_account import Credentials
from gspread_formatting import set_frozen, format_cell_range, CellFormat, Color, TextFormat
from datetime import datetime
import time

class GoogleSheetUpdater:
    def __init__(self, service_account_info):
        #self.config = config
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_info(service_account_info, scopes=scope)
        self.client = gspread.authorize(credentials)

    def ensure_sheet_exists(self):
        """Vérifie si la feuille existe, sinon la crée et la partage."""
        sheet_name = self.config['sheet_name'][0]
        emails_to_share = self.config['share_emails']

        try:
            gsheet = self.client.open(sheet_name)
        except gspread.SpreadsheetNotFound:
            gsheet = self.client.create(sheet_name)
            print(f"Feuille '{sheet_name}' créée.")

            # Partager avec les utilisateurs spécifiés dans le fichier de configuration
            for email in emails_to_share:
                gsheet.share(email, perm_type='user', role='writer')
                print(f"Feuille partagée avec '{email}'.")

        return gsheet

    def del_existing_sheet(self,gsheet):
        if self.prev != "":
          current_sheet = gsheet.worksheet(self.prev)
          gsheet.del_worksheet(current_sheet)
          print(f"Onglet '{self.prev}' supprimé .")
          self.prev=""
    def copy_existing_sheet(self, gsheet):
        """Copie l'onglet existant s'il est présent."""
        try:
            current_sheet = gsheet.worksheet(self.config['sheet_tab'])
            new_name = f"{self.config['sheet_tab']}prev{datetime.now().strftime('%y%m%d%H%M%S')}"
            self.prev=new_name
            gsheet.duplicate_sheet(current_sheet.id, new_sheet_name=new_name)
            print(f"Onglet '{self.config['sheet_tab']}' copié en '{new_name}'.")
        except gspread.exceptions.WorksheetNotFound:
            print(f"Onglet '{self.config['sheet_tab']}' non trouvé. Un nouvel onglet sera créé.")
            #current_sheet = gsheet.add_worksheet(title=self.config['sheet_tab'], rows="100", cols="20")
            current_sheet = gsheet.add_worksheet(title=self.config['sheet_tab'], rows="2", cols="20")
            print(f"Onglet '{self.config['sheet_tab']}' créé.")
            self.format_new_sheet(current_sheet)
        
        return current_sheet

    def format_new_sheet(self, sheet):
        """Applique le formatage automatique à un nouvel onglet créé."""
        columns = ['email\liste']+self.config['columns']
        sheet.insert_rows([columns], 1)
        # Fixer la première ligne et la première colonne
        set_frozen(sheet, rows=1, cols=1)

        # Formatage automatique via Google Sheets (couleurs alternées)
        # Google Sheets applique automatiquement des couleurs alternées si vous appliquez une règle de formatage conditionnel
        rule = {
            "range": {
            "sheetId": sheet.id,
            "startRowIndex": 1
            },
            "booleanRule": {
                "condition": {
                    "type": "CUSTOM_FORMULA",
                    "values": [
                        {"userEnteredValue": "=ISEVEN(ROW())"}
                    ]
                },
                "format": {
                    "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95}
                }
            }
        }

        # Utiliser l'API pour ajouter la règle de formatage conditionnel
        requests = [
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [rule["range"]],
                        "booleanRule": rule["booleanRule"]
                    },
                    "index": 0
                }
            }
        ]
        
        body = {
            "requests": requests
        }
    
        sheet.spreadsheet.batch_update(body)
        print(f"Formatage automatique appliqué à l'onglet '{sheet.title}'.")
        

    def update_google_sheet(self, json_data,config):
      self.config=config
      """Met à jour la feuille Google avec les données JSON."""
      gsheet = self.ensure_sheet_exists()  # Vérifie si la feuille existe ou la crée
      current_sheet = self.copy_existing_sheet(gsheet)

      # Obtenir les en-têtes existants
      existing_headers = current_sheet.row_values(1)[1:]
      existing_keys = current_sheet.col_values(1)[1:]

      
      for key,vals in json_data['vals']:
         if key not in existing_keys:
            new_row_index = len(existing_keys) + 2
            current_sheet.update_cell(new_row_index, 1, key)
            existing_keys.append(key)
            self.prev=""
      for key,idx in enumerate(existing_keys,1):
         if key not in json_data['vals']:
            existing_keys.pop(idx)
            current_sheet.del_row(idx)
 
      # Mettre à jour les lignes ou ajouter de nouvelles lignes si nécessaire
      lesemails = current_sheet.col_values(1)
      lesemails[2:]
      print(lesemails)
      for key, vals in json_data['vals'].items():
        try: 
           row_index = lesemails.index(key)   # +1 pour convertir en index de ligne de Google Sheets
           print(f"Found '{key}' in Row {row_index}, Column 1")
        except ValueError:
            print(f"'{key}' not found in the first column")
            new_row_index = len(lesemails) + 1
            current_sheet.update_cell(new_row_index, 1, key)
            row_index = new_row_index
            lesemails.append(key)
            self.prev=""
        cur_row=current_sheet.row_values(row_index)
        cell = current_sheet.find(key)
        if cell:
            row_index = cell.row
        else:
            # Ajouter une nouvelle ligne à la fin pour la nouvelle clé
            new_row_index = len(current_sheet.get_all_values()) + 1
            current_sheet.update_cell(new_row_index, 1, key)
            row_index = new_row_index
            self.prev=""
        for col_idx, header in enumerate(columns, start=0):
           if  header in  vals:
              if cur_row[col_idx] == '':
                current_sheet.update_cell(row_index, col_idx+1, 'X')
                self.prev=""
           else:
              if cur_row[col_idx] != 'X':
                current_sheet.update_cell(row_index, col_idx+1, '')
                self.prev=""

        # Remplir les colonnes correspondant aux éléments de la liste
        for item in vals:
            if item in columns:
                col_idx = columns.index(item) + 2  # +2 pour compenser la colonne des clés
                current_sheet.update_cell(row_index, col_idx, 'X')
        '''

      # Assurer que les nouveaux en-têtes sont bien visibles
      current_sheet.format('1:1', {'textFormat': {'bold': True}})
      #self.del_existing_sheet(gsheet)

      # Afficher le lien vers la feuille
      print(f"Lien vers la feuille : https://docs.google.com/spreadsheets/d/{gsheet.id}")

