import os
from dotenv import find_dotenv, load_dotenv

# loads environment variables; ACCESS_TOKEN

env_file_path = find_dotenv()


load_dotenv(env_file_path)

BOT_TOKEN = os.getenv('bot_token')
ACCESS_TOKEN = os.getenv('access_token')