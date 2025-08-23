'''
Purpose: provide a module for email notifications in more 
general use, however still requires app passwords and 2FA
'''
import smtplib
import logging
import ssl

from email.message import EmailMessage
from alerts.alerts import BaseAlert

logger = logging.getLogger(__name__)

defaults = {
    "gmail": {
        "host": "smtp.gmail.com",
        'port': 587
    },
    "outlook": {
        "host": "smtp.office365.com",
        'port': 587
    }
}

class EmailAlert(BaseAlert):
    '''
    Class to handle email alerts through smtp servers
    Forgoes the need to get OAuth2 authentification from google workspace
    User provides own email + smtp server
    '''

    def __init__(self) -> None:
        from utils.env_vars import EMAIL_PASS, BOT_EMAIL, PROVIDER
        self.valid = False
        if EMAIL_PASS and BOT_EMAIL:
            self.password = EMAIL_PASS
            self.username = BOT_EMAIL
            self.provider = PROVIDER
            self.valid = True

    def send_msg(self, msg: str, recipient: str, subject: str):
        if not self.valid:
            logger.error('Invalid setup: either missing mail password or mail username')
            return
    
        mail = EmailMessage()

        # set headers
        mail['To'] = recipient
        mail['From'] = self.username 
        mail['Subject'] = subject
        
        # set content
        mail.set_content(msg)

        # TODO: consider adding some visuals to notification email

        config = defaults[self.provider]
        context = ssl.create_default_context()

        with smtplib.SMTP(config['host'], config['port']) as server:
            server.starttls(context = context)
            server.login(self.username, self.password)
            server.send_message(mail)
        




