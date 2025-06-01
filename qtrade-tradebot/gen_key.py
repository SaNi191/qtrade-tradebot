# only use once


from cryptography.fernet import Fernet

print(Fernet.generate_key().decode())

# result stored in .env