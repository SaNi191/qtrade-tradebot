import os
from dotenv import find_dotenv, load_dotenv

env_file_path = find_dotenv()


load_dotenv(env_file_path)

BOT_TOKEN = os.getenv('bot_token')