import os
from dotenv import find_dotenv, load_dotenv

# Purpose: loads environment variables;

env_file_path = find_dotenv()

load_dotenv(env_file_path)

REFRESH_TOKEN = os.getenv('refresh_token')
ENCRYPTION_KEY_STR = os.getenv('encryption_key')
PATH_TO_TOKEN = os.getenv('TOKEN_PATH')
PATH_TO_CRED = os.getenv('CRED_PATH')
BOT_EMAIL = os.getenv('BOT_EMAIL')
STOPLOSS_RATIO = os.getenv('STOP_LOSS')
EMAIL_TO_NOTIFY = os.getenv('USER_EMAIL')

if ENCRYPTION_KEY_STR is None:
    # should not occur
    raise Exception('Encryption Key was not Found!')

else:
    ENCRYPTION_KEY = ENCRYPTION_KEY_STR.encode()

