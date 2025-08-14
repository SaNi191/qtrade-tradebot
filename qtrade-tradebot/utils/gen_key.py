# Purpose: only used once to generate encryption key to be stored in .env

from cryptography.fernet import Fernet

print(Fernet.generate_key().decode())
