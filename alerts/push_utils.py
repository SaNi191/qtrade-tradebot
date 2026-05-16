import requests
import logging
from alerts.base import BaseAlert

logger = logging.getLogger(__name__)

class NTFYAlert(BaseAlert):
    def __init__(self):
        self._configured = False

    def configure(self, channel):
        self._channel = channel
        self._configured = True

    def send_msg(self, msg: str,  recipient: str, subject: str): 
        if not self._configured:
            logger.error('Invalid: not yet configured!')
            return False

        header = {
            'Title': subject,
            'Priority': 'high',
            'Tags': 'rotating_light'
        }
        url = f'https://ntfy.sh/{self._channel}'
        response = requests.post(url, data = msg, headers = header)

        if response.ok:
            return True
        else:
            return False
        
