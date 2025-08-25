# TODO: add SMSALert functionality
import requests
from alerts.base import BaseAlert

class NTFYAlert(BaseAlert):
    def __init__(self):
        from utils.env_vars import SUBSCRIBED_CHANNEL
        self.channel = SUBSCRIBED_CHANNEL

    def send_msg(self, msg:str,  recipient:str, subject:str): 
        # recipient unused

        header = {
            'Title': subject,
            'Priority': 'high',
            'Tags': 'rotating_light'
        }
        url = 'https://nfty.sh/{self.channel}'
        requests.post(url, data = msg, headers = header)
        

    def _channel_reminder(self):
        print('Please provide a NTFY channel in .env')