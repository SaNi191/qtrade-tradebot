import os
from dotenv import find_dotenv, load_dotenv

# Purpose: loads environment variables;

env_file_path = find_dotenv()

load_dotenv(env_file_path)

def getenv_strict(env_var) -> str:
    var = os.getenv(env_var)
    if not var:
        raise RuntimeError(f'{env_var} not defined!')
    else:
        return var

REFRESH_TOKEN = getenv_strict('refresh_token')
ENCRYPTION_KEY_STR = getenv_strict('encryption_key')
PATH_TO_TOKEN = os.getenv('TOKEN_PATH')
PATH_TO_CRED = os.getenv('CRED_PATH')
BOT_EMAIL = getenv_strict('BOT_EMAIL')
EMAIL_PASS = getenv_strict('EMAIL_PASSWORD')
STOPLOSS_RATIO = getenv_strict('STOP_LOSS')
PROVIDER = getenv_strict('PROVIDER')

# if no notification email is specified: send to self
EMAIL_TO_NOTIFY = getenv_strict('USER_EMAIL') or BOT_EMAIL


if ENCRYPTION_KEY_STR is None:
    # should not occur
    raise Exception('Encryption Key was not Found!')

else:
    ENCRYPTION_KEY = ENCRYPTION_KEY_STR.encode()

