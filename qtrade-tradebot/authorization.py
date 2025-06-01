from env_vars import ACCESS_TOKEN
import requests

print(repr(ACCESS_TOKEN))
print(f'https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token={ACCESS_TOKEN}')
result = requests.get(f'https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token={ACCESS_TOKEN}')
result.raise_for_status()

print(result)