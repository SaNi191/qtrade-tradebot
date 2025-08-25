import requests
import logging
from alerts.base import BaseAlert


logger = logging.getLogger(__name__)

class DiscordAlert(BaseAlert):
    def __init__(self):
        self.configured = False

    def configure(self, webhook_url):
        self.destination = webhook_url
        self.configured = True

    def send_msg(self, msg: str, recipient: str | None = None, subject: str | None = None):
        if not self.configured:
            logger.error('Invalid: not yet configured!')
            return False
        header = {
            'content-type': 'application/json',
        }

        payload = {
            'content': msg
        }

        response = requests.post(self.destination, headers = header, json = payload)

        if response.status_code == 204:
            return True
        else:
            return False

