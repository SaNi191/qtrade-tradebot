import os
from email.message import EmailMessage

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



from .alerts import BaseAlert

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

PATH_TO_TOKEN = os.getenv('TOKEN_PATH')
PATH_TO_CRED = os.getenv('CRED_PATH')


class EmailAlert(BaseAlert):
    def __init__(self) -> None:
        self.creds = self.get_creds()
        self.service = build('gmail', 'v1', credentials = self.creds)


    def get_creds(self):
        # retrieve credentials and return a Credentials instance
        creds = None

        if PATH_TO_TOKEN and os.path.exists(PATH_TO_TOKEN):
            creds = Credentials.from_authorized_user_file(PATH_TO_TOKEN)
        
        if not creds or not creds.valid:
            # creds was not found or creds invalid, use credentials to validate

            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            
            else:
                flow = InstalledAppFlow.from_client_secrets_file(PATH_TO_CRED, SCOPES)
                creds = flow.run_local_server()

                if PATH_TO_TOKEN:
                    with open(PATH_TO_TOKEN, 'w') as f:
                        f.write(creds.to_json())
                else:
                    raise RuntimeError("Token Path Undefined")
                
        # TODO: store token creds in db using token_manager
        return creds



    def send_msg(self, msg:str,  recipient:str, subject:str):
        mail = EmailMessage()

        # TODO: configure email, send mail using gmail api
        

