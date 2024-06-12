import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import redis

session = []

class AccountSecurity:
    def generate_keys():
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return private_key, public_key

    def encrypt_message(public_key, message):
        rsa_key = RSA.import_key(public_key)
        cipher = PKCS1_OAEP.new(rsa_key)
        encrypted_message = cipher.encrypt(message.encode())
        return encrypted_message

    def decrypt_message(private_key, encrypted_message):
        rsa_key = RSA.import_key(private_key)
        cipher = PKCS1_OAEP.new(rsa_key)
        decrypted_message = cipher.decrypt(encrypted_message).decode()
        return decrypted_message


    # private_key, public_key = generate_keys()
    # print("Generated Private Key:")
    # print(private_key.decode())

    # print("\nGenerated Public Key:")
    # print(public_key.decode())

    # message = input("\nEnter the message to encrypt: ")
    # encrypted_message = encrypt_message(public_key, message)
    # print("\nEncrypted Message:")
    # print(encrypted_message)

    # decrypted_message = decrypt_message(private_key, encrypted_message)
    # print("\nDecrypted Message:")
    # print(decrypted_message)