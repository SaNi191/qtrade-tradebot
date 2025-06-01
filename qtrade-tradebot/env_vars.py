import os
from dotenv import find_dotenv, load_dotenv

# loads environment variables; ACCESS_TOKEN

env_file_path = find_dotenv()


load_dotenv(env_file_path)

BOT_TOKEN = os.getenv('bot_token')
ACCESS_TOKEN = os.getenv('access_token')
ENCRYPTION_KEY_STR = os.getenv('encryption_key')

if ENCRYPTION_KEY_STR is None:
    # should not occur
    raise Exception('Encryption Key was not Found!')

else:
    ENCRYPTION_KEY = ENCRYPTION_KEY_STR.encode()

