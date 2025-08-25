import requests
import logging
from alerts.base import BaseAlert


logger = logging.getLogger(__name__)

class DiscordAlert(BaseAlert):
    def __init__(self):
        # get destination from environment
        from utils.env_vars import WEB_HOOK_URL
        self.destination = WEB_HOOK_URL

    def send_msg(self, msg: str, recipient: str | None, subject: str | None):
        header = {
            'content-type': 'application/json',
        }

        payload = {
            'content': msg
        }
        response = requests.post(self.destination, headers = header, json = payload)
        logger.info(response)

