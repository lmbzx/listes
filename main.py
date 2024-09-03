from sheet_manager import SheetManager
import sys

def main():
    # Fichier JSON contenant les données
    json_file = sys.argv[1]

    # Initialisation
    sheet_manager = SheetManager('gk.jz', 'f.conf', json_file)

    # Charger le JSON et mettre à jour la feuille Google
    sheet_manager.run()

    # Optionnel : Sauvegarder un nouveau JSON (si nécessaire)
    '''
    new_json_data = {
        "listes": ["a", "b", "c", "d", "e", "f"],
        "vals": {"k0": ["a", "b", "d"], "k1": ["a", "c", "d", "f"]}
    }
    sheet_manager.save_json(new_json_data)
    '''

if __name__ == '__main__':
    main()

