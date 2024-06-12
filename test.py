from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

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


private_key, public_key = generate_keys()
print("Generated Private Key:")
print(private_key.decode())

print("\nGenerated Public Key:")
print(public_key.decode())

message = input("\nEnter the message to encrypt: ")
encrypted_message = encrypt_message(public_key, message)
print("\nEncrypted Message:")
print(encrypted_message)

decrypted_message = decrypt_message(private_key, encrypted_message)
print("\nDecrypted Message:")
print(decrypted_message)
test = b'0\x82\x01"0\r\x06\t*\x86H\x86\xf7\r\x01\x01\x01\x05\x00\x03\x82\x01\x0f\x000\x82\x01\n\x02\x82\x01\x01\x00\xb5\xf6OY\x7fs\xa2>\xda\xaa\xb0wHt \xd8\x8b\xf8.vn\xd3X\x83\\\xf1\'\x9b\x0c\xf5]\xb3\xf9\xa3\xb7\x12\xfd\x11-q)\xb8\x82GAq\xees\x99\xd0Q\x08\xd5q\x83p\x0b\xa5?\x9e(\xf1\xf8\x05\xf5\x8a\x9fAU\xb1H\xf2*;_y~\x8a*\xa4\x8f#\xf4\xcc\xcd{\x0f\xbec\xfb\x07a%\xde\x95\xcf9\xf4\xff~\x10\x1a\xff\xfd\xb0\x04\xd0\x04\xd9@\xf5\xb3\xdaHJX,\xa0U\x13\x17\xfeU\x1f)iL\x93\xb4\xfc\xde\xbf\x16[MQW_AJo\xb5\xde\xd0\xd0i?\x92&\x1d\t\xdd\x115-V\x01\x80\xd2\x12\x92\xe7)r\x1d\xd6O\xac\xb5W\x7f\xb5\x94\x05@\xec\xfe\xd8\xe7\xee\xc4\x19\xc9\xdd\x8d^\x04\xd7q\xc1\xef\x8b \x16\x81B\xfa\t\x1c\x95\x9e\xefm\t?q\xb3\xfa\xa12r\n\xc1\x8c\xff!d*\x87\xf2f@\xf3\x92\x8a+lBn\x7fifi\xa3\x91V\x9bk\xed\xdb;\x8aE\xacE\xd4\x16\xf7\xce%\x96\x9c\xce\xf2\x13Y\x02\x03\x01\x00\x01'
print(test.decode('utf-8'))