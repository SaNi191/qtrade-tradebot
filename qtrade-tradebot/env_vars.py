import os
from dotenv import find_dotenv, load_dotenv

# Purpose: loads environment variables;

env_file_path = find_dotenv()

load_dotenv(env_file_path)

REFRESH_TOKEN = os.getenv('refresh_token')
ENCRYPTION_KEY_STR = os.getenv('encryption_key')

if ENCRYPTION_KEY_STR is None:
    # should not occur
    raise Exception('Encryption Key was not Found!')

else:
    ENCRYPTION_KEY = ENCRYPTION_KEY_STR.encode()

