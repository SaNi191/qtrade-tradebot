'''
Purpose: provide a module for email notifications in more 
general use, however still requires app passwords and 2FA

Only supports gmail or outlook
'''
import smtplib
import logging
import ssl

from email.message import EmailMessage
from alerts.base import BaseAlert

logger = logging.getLogger(__name__)

'''
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
'''

class EmailAlert(BaseAlert):
    '''
    Class to handle email alerts through smtp servers
    Forgoes the need to get OAuth2 authentification from google workspace
    User provides own email + smtp server
    '''

    def __init__(self) -> None:
        self.configured = False

    
    def configure(self, username, password, host, port):
        '''
        Purpose: provides method to set config values instead of pulling from 
        environment on initialization. 
        Assumes that this information will be provided externally and simplifies testing
        '''

        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.configured = True

    def send_msg(self, msg: str, recipient: str, subject: str):
        if not self.configured:
            logger.error('Invalid: not yet configured!')
            return False
    
        mail = EmailMessage()

        # set headers
        mail['To'] = recipient
        mail['From'] = self.username 
        mail['Subject'] = subject
        
        # set content
        mail.set_content(msg)

        # TODO: consider adding some visuals to notification email


        context = ssl.create_default_context()

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls(context = context)
                server.login(self.username, self.password)
                server.send_message(mail)
            return True
    
        except Exception as e: 
            logger.error('Error Occurred: {e}')
            return False

        




