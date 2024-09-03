import os
import sys
import json
#from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
#from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode

class ServiceAccountManager:
    def __init__(self, encrypted_key_path, aes_key):
        self.encrypted_key_path = encrypted_key_path
        # Ajuster la taille de la clé AES pour qu'elle corresponde à une taille valide (16, 24, ou 32 octets)
        #self.aes_key = self.adjust_key_length(aes_key)
        self.aes_key = aes_key.ljust(16, '\0')[:16].encode('utf-8')  # Ajuster la clé à 16 octets


    def encrypt(self):
        with open(self.encrypted_key_path, 'rb') as file:
            data = file.read()
        
        
        cipher = AES.new(self.aes_key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data, AES.block_size))
        iv = b64encode(cipher.iv).decode('utf-8')
        ct = b64encode(ct_bytes).decode('utf-8')
        
        f=self.encrypted_key_path
        with open(f"{f}.x", 'w') as file_enc:
            file_enc.write(f"{iv}:{ct}")
        print(f"Fichier '{f}' chiffré et sauvegardé sous '{f}.x'")
        

    def decrypt_service_account_key(self):
        f=f"{self.encrypted_key_path}.x"
        with open(f, 'r') as file_enc:
            iv, ct = file_enc.read().split(':')
        
        iv = b64decode(iv)
        ct = b64decode(ct)
        
        cipher = AES.new(self.aes_key, AES.MODE_CBC, iv)
        data = unpad(cipher.decrypt(ct), AES.block_size)
        
        print(f"Fichier '{f}' déchiffré avec succès.")
        #print(data)
        return json.loads(data.decode('utf-8') ) # Retourner le contenu déchiffré

def main():

    passphrase = os.getenv('PASS_AES')
    if not passphrase:
            raise ValueError("La variable d'environnement PASS_AES n'est pas définie.")
 
    fichier = sys.argv[1]
    manager = ServiceAccountManager(fichier,passphrase)

    # Chiffrer le fichier
    manager.encrypt()

    # Déchiffrer le fichier et obtenir le contenu
    contenu = manager.decrypt_service_account_key()
    print("Contenu du fichier déchiffré:")
    print(contenu)

if __name__ == '__main__':
    main()
